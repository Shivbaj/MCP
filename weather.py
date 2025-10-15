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
USER_AGENT = "MCP-Weather-Server/1.0"
WTTR_API_BASE = "https://wttr.in"

# Rate limiting
request_counts: Dict[str, list] = {}


def rate_limit(max_requests: int = 60, window_seconds: int = 60):
    """Rate limiting decorator."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            client_id = "default"  # In production, extract from request
            current_time = time.time()
            
            if client_id not in request_counts:
                request_counts[client_id] = []
            
            # Remove old requests outside the window
            request_counts[client_id] = [
                req_time for req_time in request_counts[client_id]
                if current_time - req_time < window_seconds
            ]
            
            # Check if rate limit exceeded
            if len(request_counts[client_id]) >= max_requests:
                logger.warning(f"Rate limit exceeded for client: {client_id}")
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            # Add current request
            request_counts[client_id].append(current_time)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class LocationInput(BaseModel):
    """Input validation for location data."""
    latitude: float
    longitude: float
    
    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90 degrees')
        return v
    
    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180 degrees')
        return v


class CityInput(BaseModel):
    """Input validation for city names."""
    city: str
    
    @field_validator('city')
    @classmethod
    def validate_city(cls, v):
        if not v or not v.strip():
            raise ValueError('City name cannot be empty')
        
        # Basic sanitization - remove potentially harmful characters
        sanitized = re.sub(r'[<>"\';]', '', v.strip())
        if len(sanitized) > 100:
            raise ValueError('City name too long')
        
        return sanitized


class StateInput(BaseModel):
    """Input validation for US state codes."""
    state: str
    
    @field_validator('state')
    @classmethod
    def validate_state(cls, v):
        if not v or len(v) != 2:
            raise ValueError('State must be a 2-letter code')
        
        # Validate against known US state codes
        valid_states = {
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        }
        
        if v.upper() not in valid_states:
            raise ValueError('Invalid US state code')
        
        return v.upper()



async def make_api_request(
    url: str, 
    headers: Dict[str, str], 
    timeout: float = 30.0,
    max_retries: int = 3
) -> Optional[Dict[str, Any]]:
    """Make an API request with comprehensive error handling and retries."""
    
    retry_count = 0
    while retry_count < max_retries:
        try:
            async with httpx.AsyncClient() as client:
                logger.debug(f"Making API request to: {url}")
                response = await client.get(url, headers=headers, timeout=timeout)
                
                # Log response for debugging
                logger.debug(f"Response status: {response.status_code}")
                
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"Successfully fetched data from {url}")
                return data
                
        except httpx.TimeoutException:
            logger.warning(f"Timeout on request to {url} (attempt {retry_count + 1})")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {url}")
            # Don't retry on client errors (4xx)
            if 400 <= e.response.status_code < 500:
                break
        except Exception as e:
            logger.error(f"Unexpected error requesting {url}: {type(e).__name__}: {e}")
        
        retry_count += 1
        if retry_count < max_retries:
            await asyncio.sleep(2 ** retry_count)  # Exponential backoff
    
    logger.error(f"Failed to fetch data from {url} after {max_retries} attempts")
    return None


async def make_nws_request(url: str) -> Optional[Dict[str, Any]]:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    
    config = config_manager.get_server_config()
    return await make_api_request(url, headers, config.timeout, config.retry_count)

def format_alert(feature: Dict[str, Any]) -> str:
    """Format an alert feature into a readable string with proper sanitization."""
    try:
        props = feature.get("properties", {})
        
        # Sanitize text fields to prevent injection attacks
        def sanitize_text(text: str) -> str:
            if not text or not isinstance(text, str):
                return "Unknown"
            return re.sub(r'[<>"\';]', '', text.strip())[:500]  # Limit length
        
        event = sanitize_text(props.get('event'))
        area = sanitize_text(props.get('areaDesc'))
        severity = sanitize_text(props.get('severity'))
        description = sanitize_text(props.get('description'))
        instruction = sanitize_text(props.get('instruction'))
        
        return f"""Event: {event}
Area: {area}
Severity: {severity}
Description: {description}
Instructions: {instruction}"""
    
    except Exception as e:
        logger.error(f"Error formatting alert: {e}")
        return "Error formatting alert information"


@mcp.tool()
@rate_limit(max_requests=30, window_seconds=60)
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY, TX)
    
    Returns:
        String containing formatted weather alerts or error message
    
    Raises:
        ValueError: If state code is invalid
        HTTPException: If rate limit exceeded
    """
    try:
        # Validate input
        validated_input = StateInput(state=state)
        state_code = validated_input.state
        
        logger.info(f"Fetching weather alerts for state: {state_code}")
        
        url = f"{NWS_API_BASE}/alerts/active/area/{state_code}"
        data = await make_nws_request(url)

        if not data:
            logger.warning(f"No data received for alerts in state: {state_code}")
            return f"Unable to fetch weather alerts for {state_code}. The service may be temporarily unavailable."

        features = data.get("features", [])
        
        if not features:
            logger.info(f"No active alerts found for state: {state_code}")
            return f"No active weather alerts for {state_code}."

        # Format alerts with error handling for each
        alerts = []
        for feature in features[:10]:  # Limit to 10 alerts to prevent overwhelming response
            try:
                formatted_alert = format_alert(feature)
                alerts.append(formatted_alert)
            except Exception as e:
                logger.error(f"Error formatting individual alert: {e}")
                continue
        
        if not alerts:
            return f"Weather alerts were found for {state_code} but could not be formatted properly."
        
        result = "\n" + "="*50 + "\n".join(alerts)
        logger.info(f"Successfully returned {len(alerts)} alerts for {state_code}")
        return result
        
    except ValueError as e:
        logger.error(f"Invalid input for get_alerts: {e}")
        return f"Invalid state code: {e}"
    except Exception as e:
        logger.error(f"Unexpected error in get_alerts: {e}")
        return "An error occurred while fetching weather alerts. Please try again later."

@mcp.tool()
@rate_limit(max_requests=50, window_seconds=60)
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location using NWS API.

    Args:
        latitude: Latitude of the location (-90 to 90)
        longitude: Longitude of the location (-180 to 180)
    
    Returns:
        String containing formatted weather forecast or error message
    
    Raises:
        ValueError: If coordinates are invalid
        HTTPException: If rate limit exceeded
    """
    try:
        # Validate input coordinates
        validated_input = LocationInput(latitude=latitude, longitude=longitude)
        lat, lon = validated_input.latitude, validated_input.longitude
        
        logger.info(f"Fetching forecast for coordinates: {lat}, {lon}")
        
        # First get the forecast grid endpoint
        points_url = f"{NWS_API_BASE}/points/{lat},{lon}"
        points_data = await make_nws_request(points_url)

        if not points_data:
            logger.warning(f"No points data for coordinates: {lat}, {lon}")
            return f"Unable to fetch forecast data for location ({lat}, {lon}). This location may not be supported by NWS."

        properties = points_data.get("properties", {})
        forecast_url = properties.get("forecast")
        
        if not forecast_url:
            logger.error(f"No forecast URL in points response for {lat}, {lon}")
            return f"Forecast not available for this location ({lat}, {lon}). This may be outside US coverage."

        # Get the detailed forecast
        forecast_data = await make_nws_request(forecast_url)

        if not forecast_data:
            logger.warning(f"No forecast data from URL: {forecast_url}")
            return "Unable to fetch detailed forecast. Please try again later."

        # Format the periods into a readable forecast
        periods = forecast_data.get("properties", {}).get("periods", [])
        
        if not periods:
            return "No forecast periods available for this location."
        
        forecasts = []
        for period in periods[:5]:  # Only show next 5 periods
            try:
                name = period.get('name', 'Unknown period')
                temp = period.get('temperature', 'Unknown')
                temp_unit = period.get('temperatureUnit', 'F')
                wind_speed = period.get('windSpeed', 'Unknown')
                wind_dir = period.get('windDirection', 'Unknown')
                detailed = period.get('detailedForecast', 'No details available')
                
                # Sanitize forecast text
                detailed = re.sub(r'[<>"\';]', '', detailed)[:500]
                
                forecast = f"""{name}:
Temperature: {temp}°{temp_unit}
Wind: {wind_speed} {wind_dir}
Forecast: {detailed}"""
                
                forecasts.append(forecast)
                
            except Exception as e:
                logger.error(f"Error formatting forecast period: {e}")
                continue
        
        if not forecasts:
            return "Forecast data was found but could not be formatted properly."
        
        result = "\n" + "="*30 + "\n".join(forecasts)
        logger.info(f"Successfully returned forecast for {lat}, {lon}")
        return result
        
    except ValueError as e:
        logger.error(f"Invalid coordinates for get_forecast: {e}")
        return f"Invalid coordinates: {e}"
    except Exception as e:
        logger.error(f"Unexpected error in get_forecast: {e}")
        return "An error occurred while fetching the weather forecast. Please try again later."


@mcp.tool()
@rate_limit(max_requests=40, window_seconds=60)
async def get_weather(city: str) -> Dict[str, Any]:
    """Get current weather for a city using wttr.in API.
    
    Args:
        city: Name of the city (e.g., "London", "New York", "Paris")
    
    Returns:
        Dictionary containing current weather information or error details
    
    Raises:
        ValueError: If city name is invalid
        HTTPException: If rate limit exceeded
    """
    try:
        # Validate and sanitize input
        validated_input = CityInput(city=city)
        city_name = validated_input.city
        
        logger.info(f"Fetching current weather for city: {city_name}")
        
        # Make request to wttr.in API
        headers = {"User-Agent": USER_AGENT}
        url = f"{WTTR_API_BASE}/{city_name}?format=j1"
        
        config = config_manager.get_server_config()
        data = await make_api_request(url, headers, config.timeout, config.retry_count)
        
        if not data:
            logger.warning(f"No weather data received for city: {city_name}")
            return {
                "error": f"Unable to fetch weather data for {city_name}",
                "city": city_name,
                "status": "unavailable"
            }
        
        # Extract current weather information safely
        try:
            current_condition = data.get("current_condition", [{}])[0]
            nearest_area = data.get("nearest_area", [{}])[0]
            
            result = {
                "city": city_name,
                "location": {
                    "area_name": nearest_area.get("areaName", [{}])[0].get("value", city_name),
                    "country": nearest_area.get("country", [{}])[0].get("value", "Unknown"),
                    "region": nearest_area.get("region", [{}])[0].get("value", "Unknown")
                },
                "current": {
                    "temperature_c": current_condition.get("temp_C", "Unknown"),
                    "temperature_f": current_condition.get("temp_F", "Unknown"),
                    "feels_like_c": current_condition.get("FeelsLikeC", "Unknown"),
                    "feels_like_f": current_condition.get("FeelsLikeF", "Unknown"),
                    "humidity": current_condition.get("humidity", "Unknown"),
                    "wind_speed_kmh": current_condition.get("windspeedKmph", "Unknown"),
                    "wind_speed_mph": current_condition.get("windspeedMiles", "Unknown"),
                    "wind_direction": current_condition.get("winddir16Point", "Unknown"),
                    "pressure": current_condition.get("pressure", "Unknown"),
                    "visibility": current_condition.get("visibility", "Unknown"),
                    "uv_index": current_condition.get("uvIndex", "Unknown"),
                    "description": current_condition.get("weatherDesc", [{}])[0].get("value", "Unknown"),
                    "local_time": current_condition.get("localObsDateTime", "Unknown")
                },
                "status": "success",
                "data_source": "wttr.in"
            }
            
            logger.info(f"Successfully returned weather data for {city_name}")
            return result
            
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Error parsing weather data for {city_name}: {e}")
            return {
                "error": "Weather data was received but could not be parsed properly",
                "city": city_name,
                "status": "parse_error"
            }
            
    except ValueError as e:
        logger.error(f"Invalid city name for get_weather: {e}")
        return {
            "error": f"Invalid city name: {e}",
            "city": city,
            "status": "invalid_input"
        }
    except Exception as e:
        logger.error(f"Unexpected error in get_weather: {e}")
        return {
            "error": "An error occurred while fetching weather data",
            "city": city,
            "status": "server_error"
        }


def setup_middleware(app: FastAPI) -> None:
    """Setup production middleware for security and CORS."""
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
    
    # Trusted host middleware for production
    if config_manager.is_production():
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=security_config.allowed_origins + ["localhost", "127.0.0.1"]
        )


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


def main():
    """Initialize and run the production weather server."""
    logger.info("Starting Production Weather MCP Server...")
    
    app = create_app()
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
        """Endpoint for weather alerts data."""
        try:
            state = request.get("state")
            if not state:
                return {"error": "State parameter required", "status": "bad_request"}
            result = await get_alerts(state)
            return result
        except Exception as e:
            logger.error(f"Error in alerts endpoint: {e}")
            return {"error": "Internal server error", "status": "server_error"}
    
    # Run the server with production settings
    logger.info(f"Starting server on {server_config.host}:{server_config.port}")
    
    try:
        uvicorn_config = {
            "app": app,
            "host": server_config.host,
            "port": server_config.port,
            "access_log": not config_manager.is_production(),
            "log_level": "info" if config_manager.is_production() else "debug",
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