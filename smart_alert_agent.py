"""
Smart Alert Coordinator - Agent-to-Agent Protocol Example

This demonstrates a proactive alert system that coordinates with your weather
agent to provide intelligent, contextual alerts with minimal code changes.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import json

# Use existing infrastructure
from server_registry import registry
from simple_orchestrator import SimpleOrchestrator


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertAgent:
    """Smart alert agent that coordinates with weather agent."""
    
    def __init__(self):
        self.weather_orchestrator = SimpleOrchestrator()
        self.alert_subscriptions: Dict[str, Dict] = {}
        self.alert_history: List[Dict] = []
    
    async def setup_smart_alerts(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup intelligent alert monitoring using existing weather infrastructure."""
        
        alert_id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Process user preferences using existing orchestrator
        locations = user_config.get("locations", [])
        alert_types = user_config.get("alert_types", ["severe_weather", "temperature_extreme"])
        
        # Store subscription
        self.alert_subscriptions[alert_id] = {
            "locations": locations,
            "alert_types": alert_types,
            "thresholds": user_config.get("thresholds", {}),
            "notification_preferences": user_config.get("notifications", {"email": True}),
            "created_at": datetime.now().isoformat(),
            "active": True
        }
        
        return {
            "success": True,
            "alert_id": alert_id,
            "message": f"Smart alerts configured for {len(locations)} locations",
            "monitoring": alert_types
        }
    
    async def check_alerts_for_all_subscriptions(self) -> List[Dict[str, Any]]:
        """Check all active alert subscriptions - coordinates with weather agent."""
        
        triggered_alerts = []
        
        for alert_id, config in self.alert_subscriptions.items():
            if not config["active"]:
                continue
                
            for location in config["locations"]:
                # Use existing weather agent to get current conditions
                weather_query = f"Current weather conditions and any alerts for {location}"
                weather_result = await self.weather_orchestrator.process_query(weather_query)
                
                if weather_result["success"]:
                    # Analyze weather data for alert conditions
                    alert = await self._analyze_for_alerts(
                        location, weather_result, config, alert_id
                    )
                    if alert:
                        triggered_alerts.append(alert)
        
        return triggered_alerts
    
    async def _analyze_for_alerts(self, location: str, weather_data: Dict, config: Dict, alert_id: str) -> Optional[Dict]:
        """Analyze weather data against alert thresholds."""
        
        # Simple threshold checking - can be enhanced with ML
        thresholds = config.get("thresholds", {})
        
        # Extract key metrics from weather response (simplified)
        response_text = weather_data.get("response", "").lower()
        
        alert_conditions = []
        severity = AlertSeverity.LOW
        
        # Check for severe weather mentions
        if any(term in response_text for term in ["storm", "hurricane", "tornado", "severe", "warning"]):
            alert_conditions.append("Severe weather detected")
            severity = AlertSeverity.HIGH
        
        # Check temperature extremes
        if "extreme" in response_text or "record" in response_text:
            alert_conditions.append("Extreme temperature conditions")
            severity = AlertSeverity.MEDIUM
        
        # Check for travel disruptions
        if any(term in response_text for term in ["flight", "delay", "cancel", "closure"]):
            alert_conditions.append("Potential travel disruptions")
            severity = AlertSeverity.MEDIUM
        
        if alert_conditions:
            alert = {
                "alert_id": f"{alert_id}_{location}_{datetime.now().strftime('%H%M%S')}",
                "location": location,
                "severity": severity.value,
                "conditions": alert_conditions,
                "weather_summary": weather_data.get("response", ""),
                "timestamp": datetime.now().isoformat(),
                "subscription_id": alert_id
            }
            
            self.alert_history.append(alert)
            return alert
        
        return None
    
    async def get_personalized_recommendations(self, location: str, user_context: Dict) -> Dict[str, Any]:
        """Get personalized recommendations by coordinating weather + user preferences."""
        
        # Get weather using existing infrastructure
        weather_query = f"Detailed weather forecast for {location} for the next 3 days"
        weather_result = await self.weather_orchestrator.process_query(weather_query)
        
        if not weather_result["success"]:
            return {"success": False, "error": "Could not get weather data"}
        
        # Generate contextual recommendations
        recommendations = await self._generate_contextual_advice(
            location, weather_result, user_context
        )
        
        return {
            "success": True,
            "location": location,
            "recommendations": recommendations,
            "weather_basis": weather_result.get("response", ""),
            "user_context": user_context.get("activities", [])
        }
    
    async def _generate_contextual_advice(self, location: str, weather_data: Dict, user_context: Dict) -> List[str]:
        """Generate contextual advice based on weather and user preferences."""
        
        recommendations = []
        weather_text = weather_data.get("response", "").lower()
        activities = user_context.get("activities", [])
        
        # Activity-specific recommendations
        if "outdoor" in activities or "hiking" in activities:
            if "rain" in weather_text or "storm" in weather_text:
                recommendations.append("🌧️ Consider indoor alternatives - weather not suitable for outdoor activities")
            elif "sunny" in weather_text or "clear" in weather_text:
                recommendations.append("☀️ Perfect weather for outdoor activities - don't forget sunscreen!")
        
        if "travel" in activities or "commute" in user_context.get("concerns", []):
            if "snow" in weather_text or "ice" in weather_text:
                recommendations.append("🚗 Allow extra travel time - winter weather conditions expected")
            elif "fog" in weather_text:
                recommendations.append("🌫️ Reduced visibility expected - drive carefully")
        
        if "events" in activities:
            if "wind" in weather_text:
                recommendations.append("💨 Windy conditions - secure outdoor decorations and equipment")
        
        return recommendations or ["✅ No specific weather concerns for your planned activities"]


class AlertCoordinator:
    """Coordinates multiple alert agents and weather services."""
    
    def __init__(self):
        self.alert_agent = AlertAgent()
        self.active_monitors: Dict[str, Any] = {}
    
    async def start_continuous_monitoring(self, check_interval_minutes: int = 30):
        """Start continuous alert monitoring using agent coordination."""
        
        print(f"🚨 Starting continuous alert monitoring (checking every {check_interval_minutes} minutes)")
        
        while True:
            try:
                print(f"🔍 Checking alerts at {datetime.now().strftime('%H:%M:%S')}")
                
                # Coordinate with weather agent to check all subscriptions
                alerts = await self.alert_agent.check_alerts_for_all_subscriptions()
                
                if alerts:
                    print(f"⚠️ Found {len(alerts)} active alerts:")
                    for alert in alerts:
                        print(f"   📍 {alert['location']}: {alert['severity'].upper()} - {', '.join(alert['conditions'])}")
                else:
                    print("✅ No alerts triggered")
                
                # Wait before next check
                await asyncio.sleep(check_interval_minutes * 60)
                
            except Exception as e:
                print(f"❌ Error in alert monitoring: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry


async def demo_smart_alerts():
    """Demo the smart alert coordination system."""
    
    print("🚨 Smart Alert System Demo - Agent Coordination")
    print("=" * 60)
    
    coordinator = AlertCoordinator()
    alert_agent = coordinator.alert_agent
    
    # Setup smart alerts for demo
    user_config = {
        "locations": ["San Francisco", "New York", "Miami"],
        "alert_types": ["severe_weather", "temperature_extreme", "travel_disruption"],
        "thresholds": {
            "temperature_high": 90,
            "temperature_low": 32,
            "wind_speed": 25
        },
        "notifications": {"email": True, "sms": False},
        "activities": ["outdoor", "travel"],
        "concerns": ["commute"]
    }
    
    print("\n🔧 Setting up smart alerts...")
    setup_result = await alert_agent.setup_smart_alerts(user_config)
    print(f"✅ {setup_result['message']}")
    
    print("\n🔍 Running alert check...")
    alerts = await alert_agent.check_alerts_for_all_subscriptions()
    
    if alerts:
        print(f"\n⚠️ Active Alerts ({len(alerts)}):")
        for alert in alerts:
            print(f"\n📍 Location: {alert['location']}")
            print(f"🚨 Severity: {alert['severity'].upper()}")
            print(f"⚡ Conditions: {', '.join(alert['conditions'])}")
            print(f"📄 Summary: {alert['weather_summary'][:100]}...")
    else:
        print("\n✅ No alerts currently active")
    
    print("\n🎯 Getting personalized recommendations...")
    for location in ["San Francisco", "New York"]:
        recommendations = await alert_agent.get_personalized_recommendations(
            location, {"activities": ["outdoor", "travel"], "concerns": ["commute"]}
        )
        
        if recommendations["success"]:
            print(f"\n📍 {location} Recommendations:")
            for rec in recommendations["recommendations"]:
                print(f"   • {rec}")


if __name__ == "__main__":
    asyncio.run(demo_smart_alerts())