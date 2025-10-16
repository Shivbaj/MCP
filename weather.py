"""
Production Weather MCP Server

A production-ready weather service with comprehensive error handling,
logging, input validation, and security features.
"""

from typing import Any, Dict, Optional
import httpx
from mcp.server.fastmcp import FastMCP
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
import logging
import time
import os
from functools import wraps
import re
import asyncio
from config import config_manager, get_logger

# Initialize logger
logger = get_logger("weather_server")

# Initialize FastMCP server with production config
server_config = config_manager.get_server_config()
mcp = FastMCP(server_config.name)

# Constants
NWS_API_BASE = "https://api.weather.gov"
WTTR_API_BASE = "https://wttr.in"
DEFAULT_TIMEOUT = 10.0
RATE_LIMIT_CALLS = 60
RATE_LIMIT_WINDOW = 60

# Rate limiting storage
rate_limit_store = {}

def setup_middleware(app: FastAPI):
    """Configure FastAPI middleware for production."""
    security_config = config_manager.get_security_config()
    
    # CORS middleware
    if security_config.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=security_config.allowed_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST"],
            allow_headers=["*"],
        )
    
    # Trusted host middleware for security (only in production)
    if config_manager.is_production():
        # Use default allowed hosts if not configured
        # Include Docker service names for container-to-container communication
        allowed_hosts = ["localhost", "127.0.0.1", "weather-server", "*.example.com"]
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=allowed_hosts
        )

def rate_limit(func):
    """Decorator for rate limiting API calls."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Simple check - if rate limit is configured (> 0), enable rate limiting
        security_config = config_manager.get_security_config()
        if security_config.rate_limit_per_minute <= 0:
            return await func(*args, **kwargs)
        
        client_ip = "global"  # Simple global rate limiting
        current_time = time.time()
        
        if client_ip not in rate_limit_store:
            rate_limit_store[client_ip] = []
        
        # Clean old entries
        rate_limit_store[client_ip] = [
            t for t in rate_limit_store[client_ip] 
            if current_time - t < RATE_LIMIT_WINDOW
        ]
        
        if len(rate_limit_store[client_ip]) >= RATE_LIMIT_CALLS:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        rate_limit_store[client_ip].append(current_time)
        return await func(*args, **kwargs)
    
    return wrapper

async def make_api_request(url: str, headers: Dict[str, str] = None, timeout: float = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """Make HTTP request with proper error handling and logging."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers or {}, timeout=timeout)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error for {url}: {e.response.status_code}")
        raise HTTPException(status_code=502, detail=f"External API error: {e.response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"Request error for {url}: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except Exception as e:
        logger.error(f"Unexpected error for {url}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def make_nws_request(url: str, headers: Dict[str, str] = None, timeout: float = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """Make NWS API request with proper error handling."""
    return await make_api_request(url, headers, timeout)

@mcp.tool()
@rate_limit
async def get_weather(city: str) -> Dict[str, Any]:
    """Get current weather information for a city using wttr.in API."""
    if not city or not city.strip():
        raise HTTPException(status_code=400, detail="City name is required")
    
    city = city.strip()
    if len(city) > 100:
        raise HTTPException(status_code=400, detail="City name too long")
    
    try:
        url = f"{WTTR_API_BASE}/{city}?format=j1"
        data = await make_api_request(url)
        
        if not data or 'current_condition' not in data:
            raise HTTPException(status_code=404, detail="Weather data not found for this city")
        
        current = data['current_condition'][0]
        
        result = {
            "city": city,
            "temperature": f"{current.get('temp_C', 'N/A')}°C ({current.get('temp_F', 'N/A')}°F)",
            "condition": current.get('weatherDesc', [{}])[0].get('value', 'Unknown'),
            "humidity": f"{current.get('humidity', 'N/A')}%",
            "wind": f"{current.get('windspeedKmph', 'N/A')} km/h {current.get('winddir16Point', '')}",
            "feels_like": f"{current.get('FeelsLikeC', 'N/A')}°C ({current.get('FeelsLikeF', 'N/A')}°F)",
            "visibility": f"{current.get('visibility', 'N/A')} km",
            "pressure": f"{current.get('pressure', 'N/A')} mb",
            "uv_index": current.get('uvIndex', 'N/A'),
            "source": "wttr.in",
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
        }
        
        logger.info(f"Weather data retrieved for city: {city}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting weather for {city}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve weather data")

@mcp.tool()
@rate_limit  
async def get_forecast(latitude: float, longitude: float) -> Dict[str, Any]:
    """Get weather forecast for specific coordinates using NWS API."""
    try:
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            raise HTTPException(status_code=400, detail="Invalid coordinates")
        
        # Get forecast office and grid coordinates
        points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
        points_data = await make_api_request(points_url)
        
        if 'properties' not in points_data:
            raise HTTPException(status_code=404, detail="Location not supported by NWS")
        
        forecast_url = points_data['properties']['forecast']
        forecast_data = await make_api_request(forecast_url)
        
        periods = forecast_data.get('properties', {}).get('periods', [])[:7]  # Next 7 periods
        
        forecast_list = []
        for period in periods:
            forecast_list.append({
                "name": period.get('name', ''),
                "temperature": f"{period.get('temperature', 'N/A')}°{period.get('temperatureUnit', 'F')}",
                "wind": period.get('windSpeed', 'N/A') + ' ' + period.get('windDirection', ''),
                "forecast": period.get('shortForecast', ''),
                "detailed": period.get('detailedForecast', '')
            })
        
        result = {
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "area": points_data['properties'].get('relativeLocation', {}).get('properties', {}).get('city', 'Unknown')
            },
            "forecast": forecast_list,
            "source": "NWS API",
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
        }
        
        logger.info(f"Forecast retrieved for coordinates: {latitude}, {longitude}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting forecast for {latitude}, {longitude}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve forecast data")

@mcp.tool()
@rate_limit
async def get_alerts(state: str) -> Dict[str, Any]:
    """Get active weather alerts for a US state."""
    if not state or len(state) != 2:
        raise HTTPException(status_code=400, detail="State must be a 2-letter US state code")
    
    state = state.upper()
    
    try:
        url = f"{NWS_API_BASE}/alerts/active?area={state}"
        data = await make_api_request(url)
        
        features = data.get('features', [])
        alerts = []
        
        for feature in features[:10]:  # Limit to 10 alerts
            properties = feature.get('properties', {})
            alerts.append({
                "event": properties.get('event', 'Unknown'),
                "headline": properties.get('headline', ''),
                "description": properties.get('description', ''),
                "severity": properties.get('severity', 'Unknown'),
                "urgency": properties.get('urgency', 'Unknown'),
                "areas": ', '.join(properties.get('areaDesc', '').split('; ')[:3]),  # First 3 areas
                "effective": properties.get('effective', ''),
                "expires": properties.get('expires', ''),
                "sender": properties.get('senderName', '')
            })
        
        result = {
            "state": state,
            "alert_count": len(alerts),
            "alerts": alerts,
            "source": "NWS API",
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
        }
        
        logger.info(f"Retrieved {len(alerts)} alerts for state: {state}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alerts for state {state}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alert data")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    server_config = config_manager.get_server_config()
    
    app = FastAPI(
        title="Production Weather MCP Server",
        description="Model Context Protocol server providing weather information with enterprise-grade reliability",
        version="1.0.0",
        docs_url="/docs" if not config_manager.is_production() else None,
        redoc_url="/redoc" if not config_manager.is_production() else None,
    )
    
    # Setup middleware
    setup_middleware(app)
    
    return app

# Create the FastAPI app instance for uvicorn
app = create_app()

# Add routes to the global app instance
@app.get("/")
async def root():
    return {
        "name": "Production Weather MCP Server",
        "version": "1.0.0",
        "description": "Enterprise-grade weather information service via MCP protocol",
        "status": "running",
        "environment": config_manager.config.environment.value,
        "endpoints": ["/health", "/info", "/tools/get_weather", "/tools/get_forecast", "/tools/get_alerts"]
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check with external service validation."""
    from datetime import datetime
    import time
    
    start_time = time.time()
    
    # Test external services
    nws_status = "available"
    wttr_status = "available"
    
    try:
        # Quick test of NWS API
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{NWS_API_BASE}/alerts/active", timeout=5.0)
            if response.status_code != 200:
                nws_status = "degraded"
    except Exception as e:
        nws_status = "unavailable"
        logger.warning(f"NWS API health check failed: {e}")
    
    try:
        # Quick test of wttr.in API
        async with httpx.AsyncClient() as client:
            response = await client.get("https://wttr.in/London?format=j1", timeout=5.0)
            if response.status_code != 200:
                wttr_status = "degraded"
    except Exception as e:
        wttr_status = "unavailable"
        logger.warning(f"wttr.in API health check failed: {e}")
    
    overall_status = "healthy"
    if nws_status == "unavailable" and wttr_status == "unavailable":
        overall_status = "unhealthy"
    elif nws_status == "unavailable" or wttr_status == "unavailable":
        overall_status = "degraded"
    
    response_time = round((time.time() - start_time) * 1000, 2)
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": {
                "nws_api": nws_status,
                "wttr_in": wttr_status
            },
            "performance": {
                "response_time_ms": response_time,
                "memory_usage": "available" if overall_status != "unhealthy" else "unknown"
            },
            "server_info": {
                "environment": config_manager.config.environment.value,
                "debug_mode": config_manager.is_debug_enabled(),
                "version": "1.0.0"
            }
        }

@app.get("/health/quick")
async def quick_health_check():
    """Quick health check without external API calls"""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "server": "running",
        "version": "1.0.0"
    }

@app.get("/info")
async def server_info():
    return {
        "name": "weather-server",
        "description": "Weather information service using NWS API and wttr.in",
        "version": "1.0.0",
        "tools": [
            {
                "name": "get_weather",
                "description": "Get current weather for a city",
                "parameters": {"city": "string"}
            },
            {
                "name": "get_forecast", 
                "description": "Get weather forecast for coordinates",
                "parameters": {"latitude": "float", "longitude": "float"}
            },
            {
                "name": "get_alerts",
                "description": "Get weather alerts for a US state",
                "parameters": {"state": "string (2-letter code)"}
            }
        ],
        "capabilities": {
            "weather_data": True,
            "forecasting": True,
            "alerts": True,
            "multi_location": True
        },
        "data_sources": ["api.weather.gov", "wttr.in"],
        "tags": ["weather", "forecast", "alerts", "location"]
    }

@app.post("/tools/get_weather")
async def weather_endpoint(request: Dict[str, Any]):
    """Endpoint for current weather data."""
    try:
        city = request.get("city")
        if not city:
            return {"error": "City parameter required", "status": "bad_request"}
        result = await get_weather(city)
        return result
    except Exception as e:
        logger.error(f"Error in weather endpoint: {e}")
        return {"error": "Internal server error", "status": "server_error"}

@app.post("/tools/get_forecast") 
async def forecast_endpoint(request: Dict[str, Any]):
    """Endpoint for weather forecast data."""
    try:
        latitude = request.get("latitude")
        longitude = request.get("longitude")
        if latitude is None or longitude is None:
            return {"error": "Latitude and longitude parameters required", "status": "bad_request"}
        result = await get_forecast(latitude, longitude)
        return result
    except Exception as e:
        logger.error(f"Error in forecast endpoint: {e}")
        return {"error": "Internal server error", "status": "server_error"}

@app.post("/tools/get_alerts")
async def alerts_endpoint(request: Dict[str, Any]):
    """Endpoint for weather alerts."""
    try:
        state = request.get("state")
        if not state:
            return {"error": "State parameter required", "status": "bad_request"}
        result = await get_alerts(state)
        return result
    except Exception as e:
        logger.error(f"Error in alerts endpoint: {e}")
        return {"error": "Internal server error", "status": "server_error"}

def main():
    """Initialize and run the production weather server."""
    logger.info("Starting Production Weather MCP Server...")
    
    server_config = config_manager.get_server_config()
    security_config = config_manager.get_security_config()
    
    # Add API key validation middleware if required
    if security_config.api_key_required:
        @app.middleware("http")
        async def validate_api_key(request: Request, call_next):
            api_key = request.headers.get("X-API-Key")
            if not api_key or api_key != security_config.api_key:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Invalid or missing API key", "status": 401}
                )
            response = await call_next(request)
            return response

    try:
        # Configure uvicorn
        uvicorn_config = {
            "app": "weather:app",
            "host": server_config.host,
            "port": server_config.port,
            "log_level": "info" if config_manager.is_production() else "debug",
            "access_log": True,
            "loop": "asyncio"
        }
        
        # Add SSL settings for production if configured
        if config_manager.is_production() and os.getenv("SSL_CERT_PATH") and os.getenv("SSL_KEY_PATH"):
            uvicorn_config.update({
                "ssl_certfile": os.getenv("SSL_CERT_PATH"),
                "ssl_keyfile": os.getenv("SSL_KEY_PATH")
            })
        
        uvicorn.run(**uvicorn_config)
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

if __name__ == "__main__":
    main()