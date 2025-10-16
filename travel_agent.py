"""
Travel Planning Agent - Simplified Version without LangGraph Dependencies

This demonstrates how to add a travel planning agent that coordinates
with the existing weather agent using simple HTTP calls.
"""

from typing import Dict, List, Any, Optional
from enum import Enum
import asyncio
import httpx
from datetime import datetime, timedelta
import json
import re

try:
    from langchain_ollama import OllamaLLM
    from langchain.prompts import PromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    print("⚠️ LangChain not available - using simple HTTP-based approach")
    LANGCHAIN_AVAILABLE = False


class TravelTaskType(Enum):
    """Travel-specific task types that extend weather tasks."""
    TRAVEL_WEATHER_PLANNING = "travel_weather_planning"
    FLIGHT_WEATHER_ALERTS = "flight_weather_alerts"  
    DESTINATION_COMPARISON = "destination_comparison"
    ITINERARY_OPTIMIZATION = "itinerary_optimization"


class TravelAgent:
    """Travel planning agent that coordinates with the weather server."""
    
    def __init__(self, weather_server_url: str = None, llm_model: str = "llama3"):
        # Auto-detect the appropriate server URL based on environment
        if weather_server_url is None:
            # Default to localhost since we're likely running in the same container
            self.weather_server_url = "http://localhost:8000"
        else:
            self.weather_server_url = weather_server_url
            
        self.llm_model = llm_model
        self.llm = None
        
        if LANGCHAIN_AVAILABLE:
            try:
                # Use localhost for Ollama since it's the same container context
                self.llm = OllamaLLM(model=llm_model, base_url="http://ollama:11434")
            except Exception as e:
                print(f"⚠️ Could not connect to Ollama: {e}")
                self.llm = None
    
    async def plan_travel_with_weather(self, travel_query: str) -> Dict[str, Any]:
        """Main entry point - coordinates travel planning with weather data."""
        
        try:
            # Step 1: Extract travel context
            travel_context = await self._extract_travel_context(travel_query)
            
            # Step 2: Get weather for each destination via HTTP
            weather_results = {}
            for destination in travel_context["destinations"]:
                try:
                    weather_data = await self._get_weather_via_http(destination, travel_context['duration'])
                    weather_results[destination] = weather_data
                except Exception as e:
                    weather_results[destination] = {"error": str(e)}
            
            # Step 3: Create travel recommendation
            recommendation = await self._create_travel_recommendation(
                travel_context, weather_results, travel_query
            )
            
            return {
                "success": True,
                "travel_context": travel_context,
                "weather_data": weather_results,
                "recommendation": recommendation,
                "agent_type": "simplified_travel_agent"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Travel planning failed: {str(e)}",
                "agent_type": "simplified_travel_agent"
            }
    
    async def _extract_travel_context(self, query: str) -> Dict[str, Any]:
        """Extract travel information from query using simple pattern matching."""
        
        # Simple regex patterns for common travel queries
        destinations = []
        duration = 7  # Default week
        
        # Look for city names (simple pattern)
        city_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        potential_cities = re.findall(city_pattern, query)
        
        # Filter out common words that aren't cities
        common_words = {'Plan', 'Travel', 'Weather', 'For', 'This', 'Weekend', 'Week', 'Days', 'Trip'}
        destinations = [city for city in potential_cities if city not in common_words]
        
        # Look for time indicators
        if 'weekend' in query.lower():
            duration = 3
        elif 'week' in query.lower():
            duration = 7
        elif 'day' in query.lower():
            # Extract number of days
            day_match = re.search(r'(\d+)\s*days?', query.lower())
            if day_match:
                duration = int(day_match.group(1))
            else:
                duration = 3
        
        # Default destination if none found
        if not destinations:
            destinations = ['Tokyo']  # From the user's example
        
        return {
            "destinations": destinations,
            "duration": duration,
            "travel_type": "tourism",  # Default
            "extracted_from": query
        }
    
    async def _get_weather_via_http(self, destination: str, days: int = 7) -> Dict[str, Any]:
        """Get weather data via HTTP call to weather server."""
        
        try:
            async with httpx.AsyncClient() as client:
                # Use the working weather endpoint with proper URL
                url = f"{self.weather_server_url}/tools/get_weather"
                payload = {"city": destination}
                
                print(f"Debug: Making request to {url} with payload {payload}")
                
                response = await client.post(
                    url,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    weather_data = response.json()
                    # Add duration info for context
                    weather_data["requested_duration"] = days
                    return weather_data
                else:
                    return {"error": f"Weather API returned {response.status_code}: {response.text}"}
                    
        except Exception as e:
            return {"error": f"Failed to get weather data: {str(e)} (Type: {type(e).__name__})"}
    
    async def _create_travel_recommendation(self, travel_context: Dict, weather_results: Dict, original_query: str) -> str:
        """Create travel recommendation based on context and weather."""
        
        # Always use simple recommendation for now to avoid LLM dependency issues
        return self._create_simple_recommendation(travel_context, weather_results)
    
    async def _create_llm_recommendation(self, travel_context: Dict, weather_results: Dict, original_query: str) -> str:
        """Create recommendation using LLM."""
        
        try:
            prompt = PromptTemplate(
                input_variables=["destinations", "duration", "weather_data", "query"],
                template="""
You are a travel planning assistant. Based on the following information, provide a helpful travel recommendation:

Original Query: {query}
Destinations: {destinations}
Duration: {duration} days
Weather Data: {weather_data}

Please provide:
1. Weather-based recommendations for each destination
2. Best travel dates based on weather
3. What to pack based on forecast
4. Any weather-related travel tips

Keep the response concise and practical.
"""
            )
            
            formatted_prompt = prompt.format(
                query=original_query,
                destinations=", ".join(travel_context["destinations"]),
                duration=travel_context["duration"],
                weather_data=json.dumps(weather_results, indent=2)
            )
            
            response = await asyncio.to_thread(self.llm.invoke, formatted_prompt)
            return response
            
        except Exception as e:
            return f"LLM recommendation failed: {str(e)}"
    
    def _create_simple_recommendation(self, travel_context: Dict, weather_results: Dict) -> str:
        """Create simple recommendation without LLM."""
        
        recommendations = []
        recommendations.append(f"🌍 Travel Planning for {', '.join(travel_context['destinations'])}")
        recommendations.append(f"📅 Duration: {travel_context['duration']} days")
        recommendations.append("")
        
        for destination in travel_context["destinations"]:
            weather_data = weather_results.get(destination, {})
            
            if "error" in weather_data:
                recommendations.append(f"⚠️ {destination}: Could not get weather data - {weather_data['error']}")
            else:
                # Extract useful information from weather data
                recommendations.append(f"✅ {destination}: Current weather conditions")
                
                # Extract current weather information
                if 'temperature' in weather_data:
                    recommendations.append(f"   🌡️ Temperature: {weather_data['temperature']}")
                if 'condition' in weather_data:
                    recommendations.append(f"   🌤️ Conditions: {weather_data['condition']}")
                if 'humidity' in weather_data:
                    recommendations.append(f"   💧 Humidity: {weather_data['humidity']}")
                if 'wind' in weather_data:
                    recommendations.append(f"   💨 Wind: {weather_data['wind']}")
                
                # Add packing recommendations based on conditions
                condition = weather_data.get('condition', '').lower()
                if 'rain' in condition:
                    recommendations.append(f"   ☔ Pack rain gear and waterproof clothing")
                elif 'snow' in condition:
                    recommendations.append(f"   ❄️ Pack warm winter clothing")
                elif 'sun' in condition or 'clear' in condition:
                    recommendations.append(f"   ☀️ Pack sun protection and light clothing")
                
                recommendations.append(f"   🎒 Consider the weather for your {travel_context['duration']}-day trip")
                
        recommendations.append("")
        recommendations.append("💡 Travel Tips:")
        recommendations.append("   • Check weather updates before departure")
        recommendations.append("   • Pack layers for temperature changes")
        recommendations.append("   • Consider weather-appropriate activities")
        recommendations.append("   • Monitor weather alerts for your travel dates")
        
        return "\n".join(recommendations)


# For backward compatibility, export the main class
__all__ = ['TravelAgent']