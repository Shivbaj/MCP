"""
Simplified Agent Orchestrator for MCP Servers

This module provides a simplified orchestrator that can coordinate MCP servers
for agentic workflows without requiring LangGraph initially.
"""

import asyncio
import httpx
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

from server_registry import MCPServerRegistry, registry


class TaskType(Enum):
    """Types of tasks the orchestrator can handle."""
    WEATHER_QUERY = "weather_query"
    FORECAST_ANALYSIS = "forecast_analysis" 
    ALERT_MONITORING = "alert_monitoring"
    MULTI_LOCATION = "multi_location"
    GENERAL_INQUIRY = "general_inquiry"


class SimpleOrchestrator:
    """Simplified orchestrator for weather-related agentic workflows."""
    
    def __init__(self):
        self.registry = registry
    
    def _classify_task(self, query: str) -> TaskType:
        """Classify the user query to determine task type."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["forecast", "prediction", "future", "tomorrow", "week"]):
            return TaskType.FORECAST_ANALYSIS
        elif any(word in query_lower for word in ["alert", "warning", "storm", "emergency"]):
            return TaskType.ALERT_MONITORING
        elif any(word in query_lower for word in ["multiple", "compare", "cities", "locations"]):
            return TaskType.MULTI_LOCATION
        elif any(word in query_lower for word in ["weather", "temperature", "current", "now"]):
            return TaskType.WEATHER_QUERY
        else:
            return TaskType.GENERAL_INQUIRY
    
    def _extract_locations(self, query: str) -> List[str]:
        """Extract location information from the query using simple keyword matching."""
        # Simple location extraction - in production, use proper NER
        common_cities = [
            "london", "paris", "new york", "tokyo", "sydney", "berlin",
            "rome", "madrid", "amsterdam", "barcelona", "vienna", "prague",
            "moscow", "beijing", "mumbai", "delhi", "bangkok", "singapore",
            "los angeles", "chicago", "houston", "phoenix", "philadelphia",
            "san francisco", "seattle", "boston", "atlanta", "miami"
        ]
        
        us_states = [
            "california", "texas", "florida", "new york", "pennsylvania",
            "illinois", "ohio", "georgia", "north carolina", "michigan"
        ]
        
        query_lower = query.lower()
        found_locations = []
        
        # Check for cities
        for city in common_cities:
            if city in query_lower:
                # Capitalize properly
                found_locations.append(city.title())
        
        # Check for US states
        for state in us_states:
            if state in query_lower:
                found_locations.append(state.title())
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(found_locations))
    
    async def _call_weather_tool(self, city: str) -> Dict[str, Any]:
        """Call the weather tool on the weather server."""
        server = self.registry.get_server("weather-server")
        if not server:
            return {"error": "Weather server not found"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{server.base_url}/tools/get_weather",
                    json={"city": city},
                    timeout=10.0
                )
                
                # Check if request was successful
                if response.status_code != 200:
                    return {"error": f"Weather server returned status {response.status_code}: {response.text}"}
                
                # Check if response has content
                if not response.text.strip():
                    return {"error": "Weather server returned empty response"}
                
                # Try to parse JSON
                try:
                    result = response.json()
                    return result
                except Exception as json_error:
                    return {"error": f"Failed to parse weather response as JSON: {str(json_error)}. Response: {response.text[:200]}"}
                    
        except Exception as e:
            return {"error": f"Failed to call weather tool: {str(e)}"}
    
    async def _call_forecast_tool(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Call the forecast tool on the weather server."""
        server = self.registry.get_server("weather-server")
        if not server:
            return {"error": "Weather server not found"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{server.base_url}/tools/get_forecast",
                    json={"latitude": latitude, "longitude": longitude},
                    timeout=15.0
                )
                
                # Check if request was successful
                if response.status_code != 200:
                    return {"error": f"Forecast server returned status {response.status_code}: {response.text}"}
                
                # Check if response has content
                if not response.text.strip():
                    return {"error": "Forecast server returned empty response"}
                
                # Try to parse JSON
                try:
                    return response.json()
                except Exception as json_error:
                    return {"error": f"Failed to parse forecast response as JSON: {str(json_error)}. Response: {response.text[:200]}"}
                    
        except Exception as e:
            return {"error": f"Failed to call forecast tool: {str(e)}"}
    
    async def _call_alerts_tool(self, state_code: str) -> Dict[str, Any]:
        """Call the alerts tool on the weather server."""
        server = self.registry.get_server("weather-server")
        if not server:
            return {"error": "Weather server not found"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{server.base_url}/tools/get_alerts",
                    json={"state": state_code},
                    timeout=10.0
                )
                
                # Check if request was successful
                if response.status_code != 200:
                    return {"error": f"Alerts server returned status {response.status_code}: {response.text}"}
                
                # Check if response has content
                if not response.text.strip():
                    return {"error": "Alerts server returned empty response"}
                
                # Try to parse JSON
                try:
                    return response.json()
                except Exception as json_error:
                    return {"error": f"Failed to parse alerts response as JSON: {str(json_error)}. Response: {response.text[:200]}"}
                    
        except Exception as e:
            return {"error": f"Failed to call alerts tool: {str(e)}"}
    
    def _get_state_code(self, location: str) -> Optional[str]:
        """Get US state code for alert queries."""
        state_mapping = {
            "california": "CA",
            "texas": "TX", 
            "florida": "FL",
            "new york": "NY",
            "pennsylvania": "PA",
            "illinois": "IL",
            "ohio": "OH",
            "georgia": "GA",
            "north carolina": "NC",
            "michigan": "MI"
        }
        return state_mapping.get(location.lower())
    
    def _get_coordinates(self, location: str) -> Optional[tuple]:
        """Get coordinates for forecast queries (simplified mapping)."""
        coord_mapping = {
            "london": (51.5074, -0.1278),
            "paris": (48.8566, 2.3522),
            "new york": (40.7128, -74.0060),
            "tokyo": (35.6762, 139.6503),
            "sydney": (-33.8688, 151.2093),
            "berlin": (52.5200, 13.4050),
            "los angeles": (34.0522, -118.2437),
            "chicago": (41.8781, -87.6298)
        }
        return coord_mapping.get(location.lower())
    
    def _format_response(self, task_type: TaskType, data: Dict[str, Any], locations: List[str]) -> str:
        """Format the response based on task type and data."""
        
        if task_type == TaskType.WEATHER_QUERY:
            if len(locations) == 1 and locations[0].lower() in data:
                weather_data = data[locations[0].lower()]
                if "error" in weather_data:
                    return f"❌ Error getting weather for {locations[0]}: {weather_data['error']}"
                
                return f"🌤️ Current weather in {weather_data.get('city', locations[0])}:\n" \
                       f"   🌡️ Temperature: {weather_data.get('temperature', 'N/A')}°C\n" \
                       f"   📝 Conditions: {weather_data.get('description', 'N/A')}"
            
        elif task_type == TaskType.MULTI_LOCATION:
            responses = []
            for location in locations:
                if location.lower() in data:
                    weather_data = data[location.lower()]
                    if "error" not in weather_data:
                        responses.append(
                            f"🌤️ {weather_data.get('city', location)}: "
                            f"{weather_data.get('temperature', 'N/A')}°C, "
                            f"{weather_data.get('description', 'N/A')}"
                        )
                    else:
                        responses.append(f"❌ {location}: Error - {weather_data['error']}")
            
            if responses:
                return "🗺️ Weather comparison:\n" + "\n".join(f"   {resp}" for resp in responses)
        
        elif task_type == TaskType.FORECAST_ANALYSIS:
            if "forecast" in data and locations:
                forecast_data = data["forecast"]
                if isinstance(forecast_data, str) and not forecast_data.startswith("Error"):
                    return f"📅 Forecast for {locations[0]}:\n{forecast_data}"
                elif "error" in str(forecast_data):
                    return f"❌ Error getting forecast: {forecast_data}"
        
        elif task_type == TaskType.ALERT_MONITORING:
            if "alerts" in data and locations:
                alert_data = data["alerts"]
                if isinstance(alert_data, str) and "No active alerts" in alert_data:
                    return f"✅ No active weather alerts for {locations[0]}"
                elif isinstance(alert_data, str) and not alert_data.startswith("Error"):
                    return f"🚨 Weather alerts for {locations[0]}:\n{alert_data}"
                elif "error" in str(alert_data):
                    return f"❌ Error getting alerts: {alert_data}"
        
        # Fallback response
        return f"🤖 I processed your query but couldn't format a proper response. Raw data: {json.dumps(data, indent=2)}"
    
    async def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process a user query through the simplified orchestrator."""
        
        start_time = datetime.now()
        execution_log = []
        
        try:
            # Step 1: Classify task
            task_type = self._classify_task(user_query)
            execution_log.append(f"Classified task as: {task_type.value}")
            
            # Step 2: Extract locations
            locations = self._extract_locations(user_query)
            execution_log.append(f"Extracted locations: {locations}")
            
            # Step 3: Gather data based on task type
            gathered_data = {}
            
            if task_type in [TaskType.WEATHER_QUERY, TaskType.MULTI_LOCATION]:
                # Get weather for all locations
                for location in locations:
                    weather_data = await self._call_weather_tool(location)
                    gathered_data[location.lower()] = weather_data
                execution_log.append(f"Gathered weather data for {len(locations)} locations")
                
            elif task_type == TaskType.FORECAST_ANALYSIS and locations:
                # Get forecast for first location (simplified)
                coords = self._get_coordinates(locations[0])
                if coords:
                    forecast_data = await self._call_forecast_tool(coords[0], coords[1])
                    gathered_data["forecast"] = forecast_data
                    execution_log.append("Gathered forecast data")
                else:
                    gathered_data["forecast"] = {"error": "Coordinates not available for this location"}
                    execution_log.append("Could not get coordinates for forecast")
                    
            elif task_type == TaskType.ALERT_MONITORING and locations:
                # Get alerts for US states
                for location in locations:
                    state_code = self._get_state_code(location)
                    if state_code:
                        alert_data = await self._call_alerts_tool(state_code)
                        gathered_data["alerts"] = alert_data
                        execution_log.append(f"Gathered alert data for {location}")
                        break  # Only first US state for simplicity
            
            # Step 4: Format response
            response = self._format_response(task_type, gathered_data, locations)
            execution_log.append("Generated response")
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            return {
                "success": True,
                "response": response,
                "task_type": task_type.value,
                "locations": locations,
                "execution_log": execution_log,
                "execution_time": execution_time,
                "raw_data": gathered_data,
                "metadata": {
                    "timestamp": start_time.isoformat(),
                    "query": user_query
                }
            }
            
        except Exception as e:
            execution_log.append(f"Error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "execution_log": execution_log,
                "metadata": {
                    "timestamp": start_time.isoformat(),
                    "query": user_query
                }
            }


async def main():
    """Example usage of the simplified orchestrator."""
    orchestrator = SimpleOrchestrator()
    
    test_queries = [
        "What's the weather like in London?",
        "Compare weather in New York and Paris", 
        "What's the forecast for Tokyo tomorrow?",
        "Any weather alerts in California?",
    ]
    
    print("🤖 Simplified Agent Orchestrator Demo")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-" * 40)
        
        result = await orchestrator.process_query(query)
        
        if result["success"]:
            print(f"✅ Response ({result['execution_time']:.2f}s):")
            print(f"   {result['response']}")
            print(f"🏷️ Task: {result['task_type']} | Locations: {result['locations']}")
        else:
            print(f"❌ Error: {result['error']}")


if __name__ == "__main__":
    asyncio.run(main())