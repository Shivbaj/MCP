"""
Multi-Source Weather Intelligence Agent - Agent Coordination Example

This agent coordinates multiple weather data sources through your existing
MCP infrastructure to provide more reliable, consensus-based weather intelligence.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import statistics
from dataclasses import dataclass

# Reuse existing infrastructure
from weather import make_api_request, make_nws_request
from server_registry import registry


@dataclass
class WeatherConsensus:
    """Consensus weather data from multiple sources."""
    temperature: float
    humidity: float
    conditions: str
    confidence_score: float
    source_count: int
    data_sources: List[str]


class DataSource(Enum):
    """Available weather data sources."""
    NWS = "nws"          # National Weather Service
    WTTR = "wttr"        # wttr.in
    EXISTING_MCP = "mcp"  # Your existing MCP weather server


class WeatherIntelligenceAgent:
    """Coordinates multiple weather sources for enhanced accuracy."""
    
    def __init__(self):
        self.data_sources = {
            DataSource.NWS: self._fetch_nws_data,
            DataSource.WTTR: self._fetch_wttr_data,
            DataSource.EXISTING_MCP: self._fetch_mcp_data
        }
        self.source_reliability = {
            DataSource.NWS: 0.9,
            DataSource.WTTR: 0.8,
            DataSource.EXISTING_MCP: 0.85
        }
    
    async def get_consensus_weather(self, location: str) -> Dict[str, Any]:
        """Coordinate multiple data sources to get consensus weather."""
        
        print(f"🔍 Gathering weather data from multiple sources for {location}...")
        
        # Coordinate data gathering from all available sources
        source_results = {}
        for source, fetch_function in self.data_sources.items():
            try:
                print(f"   📡 Querying {source.value.upper()}...")
                data = await fetch_function(location)
                if data:
                    source_results[source] = data
                    print(f"   ✅ {source.value.upper()}: Success")
                else:
                    print(f"   ❌ {source.value.upper()}: No data")
            except Exception as e:
                print(f"   ⚠️ {source.value.upper()}: Error - {e}")
        
        if not source_results:
            return {"success": False, "error": "No weather data sources available"}
        
        # Create consensus from multiple sources
        consensus = await self._create_consensus(source_results, location)
        
        # Enhance with intelligence analysis
        intelligence_report = await self._generate_intelligence_report(consensus, source_results)
        
        return {
            "success": True,
            "location": location,
            "consensus": consensus,
            "intelligence_report": intelligence_report,
            "sources_used": len(source_results),
            "reliability_score": consensus.confidence_score,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _fetch_nws_data(self, location: str) -> Optional[Dict[str, Any]]:
        """Fetch data from National Weather Service using existing infrastructure."""
        # Simplified - in reality, you'd geocode location first
        # Using San Francisco coordinates as example
        url = "https://api.weather.gov/points/37.7749,-122.4194"
        
        points_data = await make_nws_request(url)
        if not points_data:
            return None
        
        forecast_url = points_data.get("properties", {}).get("forecast")
        if not forecast_url:
            return None
        
        forecast_data = await make_nws_request(forecast_url)
        if not forecast_data:
            return None
        
        # Extract current conditions from first forecast period
        periods = forecast_data.get("properties", {}).get("periods", [])
        if periods:
            current = periods[0]
            return {
                "temperature": current.get("temperature", 0),
                "humidity": 50,  # NWS doesn't always provide humidity
                "conditions": current.get("shortForecast", "Unknown"),
                "source": "NWS"
            }
        
        return None
    
    async def _fetch_wttr_data(self, location: str) -> Optional[Dict[str, Any]]:
        """Fetch data from wttr.in service."""
        url = f"https://wttr.in/{location}?format=j1"
        
        headers = {"User-Agent": "WeatherMCP-Intelligence/1.0"}
        data = await make_api_request(url, headers, timeout=10.0)
        
        if data and "current_condition" in data:
            current = data["current_condition"][0]
            return {
                "temperature": int(current.get("temp_F", 0)),
                "humidity": int(current.get("humidity", 0)),
                "conditions": current.get("weatherDesc", [{}])[0].get("value", "Unknown"),
                "source": "WTTR"
            }
        
        return None
    
    async def _fetch_mcp_data(self, location: str) -> Optional[Dict[str, Any]]:
        """Fetch data from existing MCP weather server."""
        server = registry.get_server("weather-server")
        if not server:
            return None
        
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{server.base_url}/tools/get_weather",
                    json={"city": location},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Extract temperature and conditions from response text
                    # This is simplified - you'd parse actual structured data
                    response_text = data.get("content", [{}])[0].get("text", "")
                    
                    # Simple extraction (could be enhanced with regex/NLP)
                    temp = 70  # Default fallback
                    conditions = "Partly Cloudy"
                    
                    if "°F" in response_text:
                        # Extract temperature
                        import re
                        temp_match = re.search(r'(\d+)°F', response_text)
                        if temp_match:
                            temp = int(temp_match.group(1))
                    
                    return {
                        "temperature": temp,
                        "humidity": 55,  # Default
                        "conditions": conditions,
                        "source": "MCP",
                        "raw_response": response_text
                    }
                    
        except Exception as e:
            print(f"Error fetching MCP data: {e}")
            
        return None
    
    async def _create_consensus(self, source_results: Dict[DataSource, Dict], location: str) -> WeatherConsensus:
        """Create consensus weather data from multiple sources."""
        
        temperatures = []
        humidities = []
        conditions = []
        sources = []
        
        for source, data in source_results.items():
            reliability = self.source_reliability[source]
            
            # Weight data by source reliability
            temp = data.get("temperature", 70)
            humidity = data.get("humidity", 50)
            
            # Add multiple weighted samples for more reliable sources
            weight = int(reliability * 10)
            temperatures.extend([temp] * weight)
            humidities.extend([humidity] * weight)
            conditions.append(data.get("conditions", "Unknown"))
            sources.append(data.get("source", source.value))
        
        # Calculate consensus values
        consensus_temp = statistics.mean(temperatures) if temperatures else 70
        consensus_humidity = statistics.mean(humidities) if humidities else 50
        
        # Simple consensus for conditions (most common)
        consensus_conditions = max(set(conditions), key=conditions.count) if conditions else "Unknown"
        
        # Calculate confidence based on source agreement
        temp_variance = statistics.variance(temperatures) if len(temperatures) > 1 else 0
        confidence = max(0.5, 1.0 - (temp_variance / 100.0))  # Lower variance = higher confidence
        
        return WeatherConsensus(
            temperature=round(consensus_temp, 1),
            humidity=round(consensus_humidity, 1),
            conditions=consensus_conditions,
            confidence_score=round(confidence, 2),
            source_count=len(source_results),
            data_sources=sources
        )
    
    async def _generate_intelligence_report(self, consensus: WeatherConsensus, source_results: Dict) -> str:
        """Generate an intelligence analysis report."""
        
        report_lines = []
        
        report_lines.append(f"🧠 Weather Intelligence Analysis")
        report_lines.append(f"📊 Data Sources: {consensus.source_count} ({', '.join(consensus.data_sources)})")
        report_lines.append(f"🎯 Confidence: {consensus.confidence_score*100:.0f}%")
        report_lines.append(f"🌡️ Consensus Temperature: {consensus.temperature}°F")
        report_lines.append(f"💧 Humidity: {consensus.humidity}%")
        report_lines.append(f"☁️ Conditions: {consensus.conditions}")
        
        # Data quality analysis
        if consensus.confidence_score > 0.8:
            report_lines.append("✅ High confidence - sources in good agreement")
        elif consensus.confidence_score > 0.6:
            report_lines.append("⚠️ Medium confidence - some variation between sources")
        else:
            report_lines.append("🔍 Lower confidence - significant variation detected")
        
        # Source comparison
        temps = [data.get("temperature", 0) for data in source_results.values()]
        if len(temps) > 1:
            temp_range = max(temps) - min(temps)
            if temp_range > 10:
                report_lines.append(f"📈 Temperature variation: {temp_range:.1f}°F across sources")
        
        return "\n".join(report_lines)


class IntelligenceCoordinator:
    """Coordinates weather intelligence across multiple agents and time periods."""
    
    def __init__(self):
        self.intelligence_agent = WeatherIntelligenceAgent()
        self.forecast_cache: Dict[str, Dict] = {}
    
    async def get_enhanced_forecast(self, location: str, days: int = 3) -> Dict[str, Any]:
        """Get enhanced forecast by coordinating multiple timeframes."""
        
        print(f"🔮 Creating enhanced {days}-day forecast for {location}")
        
        # Get current consensus as baseline
        current_weather = await self.intelligence_agent.get_consensus_weather(location)
        
        if not current_weather["success"]:
            return current_weather
        
        # Simulate multi-day coordination (in reality, you'd call multiple forecast APIs)
        enhanced_forecast = {
            "location": location,
            "current_conditions": current_weather["consensus"],
            "intelligence_summary": current_weather["intelligence_report"],
            "forecast_days": days,
            "reliability_metrics": {
                "data_sources": current_weather["sources_used"],
                "confidence_score": current_weather["reliability_score"]
            },
            "recommendations": await self._generate_forecast_recommendations(current_weather)
        }
        
        return {
            "success": True,
            "enhanced_forecast": enhanced_forecast,
            "coordination_method": "multi-source intelligence",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _generate_forecast_recommendations(self, weather_data: Dict) -> List[str]:
        """Generate actionable recommendations based on intelligence analysis."""
        
        recommendations = []
        consensus = weather_data["consensus"]
        confidence = weather_data["reliability_score"]
        
        # Temperature-based recommendations
        if consensus.temperature > 80:
            recommendations.append("🌞 Hot weather expected - stay hydrated and seek shade")
        elif consensus.temperature < 40:
            recommendations.append("🧊 Cold weather - dress warmly and check for ice")
        
        # Confidence-based recommendations
        if confidence < 0.7:
            recommendations.append("🔍 Weather prediction confidence is lower - check again closer to your plans")
        else:
            recommendations.append("✅ High confidence forecast - good for planning outdoor activities")
        
        # Conditions-based recommendations
        if "rain" in consensus.conditions.lower():
            recommendations.append("☔ Rain expected - carry an umbrella")
        elif "snow" in consensus.conditions.lower():
            recommendations.append("❄️ Snow conditions - allow extra travel time")
        
        return recommendations or ["📋 Standard weather precautions recommended"]


async def demo_intelligence_coordination():
    """Demo the weather intelligence coordination system."""
    
    print("🧠 Weather Intelligence Agent Coordination Demo")
    print("=" * 70)
    
    coordinator = IntelligenceCoordinator()
    
    test_locations = ["San Francisco", "New York"]
    
    for location in test_locations:
        print(f"\n📍 Getting intelligent weather analysis for {location}:")
        print("-" * 50)
        
        # Get consensus weather from multiple sources
        result = await coordinator.intelligence_agent.get_consensus_weather(location)
        
        if result["success"]:
            consensus = result["consensus"]
            print(f"\n🎯 Consensus Weather:")
            print(f"   Temperature: {consensus.temperature}°F")
            print(f"   Humidity: {consensus.humidity}%")
            print(f"   Conditions: {consensus.conditions}")
            print(f"   Confidence: {consensus.confidence_score*100:.0f}%")
            print(f"   Sources: {consensus.source_count} ({', '.join(consensus.data_sources)})")
            
            print(f"\n{result['intelligence_report']}")
            
            # Get enhanced forecast
            print(f"\n🔮 Enhanced Forecast Analysis:")
            forecast = await coordinator.get_enhanced_forecast(location, 3)
            
            if forecast["success"]:
                for recommendation in forecast["enhanced_forecast"]["recommendations"]:
                    print(f"   • {recommendation}")
        else:
            print(f"❌ Could not get weather intelligence: {result['error']}")


if __name__ == "__main__":
    asyncio.run(demo_intelligence_coordination())