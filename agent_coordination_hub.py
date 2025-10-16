"""
Minimal Integration Layer for Agent-to-Agent Protocols

This shows how to add agent coordination to your existing system 
with minimal changes to current code.
"""

from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime

# Import existing infrastructure
from simple_orchestrator import SimpleOrchestrator
from mcp_client import AgenticMCPClient

# Import new agents (minimal additions)
from smart_alert_agent import AlertAgent
from weather_intelligence_agent import WeatherIntelligenceAgent

# Import agent orchestrator conditionally (to avoid LangGraph issues)
try:
    from agent_orchestrator import WeatherOrchestrator, AgentState, TaskType
    LANGGRAPH_AVAILABLE = True
except ImportError:
    print("⚠️ LangGraph not fully available - using simple orchestrator only")
    LANGGRAPH_AVAILABLE = False
    # Create mock types
    class TaskType:
        WEATHER_QUERY = "weather_query"
        MULTI_LOCATION = "multi_location"

# Import travel agent conditionally
try:
    from travel_agent import TravelAgent
    TRAVEL_AGENT_AVAILABLE = True
except ImportError:
    print("⚠️ Travel agent not available - travel coordination disabled")
    TRAVEL_AGENT_AVAILABLE = False


class AgentCoordinationHub:
    """
    Central hub that coordinates multiple agents using existing infrastructure.
    This requires MINIMAL changes to your existing codebase.
    """
    
    def __init__(self, llm_model: str = "llama3"):
        # Reuse existing orchestrators
        if LANGGRAPH_AVAILABLE:
            self.weather_orchestrator = WeatherOrchestrator(llm_model)
        else:
            self.weather_orchestrator = None
        
        self.simple_orchestrator = SimpleOrchestrator()
        self.mcp_client = AgenticMCPClient()
        
        # Add new specialized agents
        if TRAVEL_AGENT_AVAILABLE:
            # Let the travel agent auto-detect the correct server URL
            self.travel_agent = TravelAgent(llm_model=llm_model)
        else:
            self.travel_agent = None
            
        self.alert_agent = AlertAgent()
        self.intelligence_agent = WeatherIntelligenceAgent()
        
        # Agent routing map (extend existing task classification)
        self.agent_routes = {
            "travel": self._route_to_travel_agent,
            "alerts": self._route_to_alert_agent,  
            "intelligence": self._route_to_intelligence_agent,
            "weather": self._route_to_weather_agent  # Existing
        }
    
    async def process_coordinated_query(self, user_query: str, coordination_type: str = "auto") -> Dict[str, Any]:
        """
        Process queries using agent coordination - extends existing process_query method.
        This is your NEW main entry point that coordinates multiple agents.
        """
        
        print(f"🤖 Coordinating agents for: '{user_query}'")
        
        # Step 1: Determine coordination strategy (minimal addition to existing classification)
        if coordination_type == "auto":
            coordination_type = await self._determine_coordination_strategy(user_query)
        
        print(f"🔄 Using coordination strategy: {coordination_type}")
        
        # Step 2: Route to appropriate agent coordinator
        if coordination_type in self.agent_routes:
            result = await self.agent_routes[coordination_type](user_query)
        else:
            # Fallback to existing weather orchestrator
            result = await self.weather_orchestrator.process_query(user_query)
            result["coordination_type"] = "single_agent"
        
        # Step 3: Add coordination metadata
        result["coordination_used"] = coordination_type
        result["timestamp"] = datetime.now().isoformat()
        
        return result
    
    async def _determine_coordination_strategy(self, query: str) -> str:
        """
        Determine which agent coordination strategy to use.
        Extends existing task classification with minimal changes.
        """
        
        query_lower = query.lower()
        
        # Multi-agent coordination triggers
        if any(word in query_lower for word in ["travel", "trip", "vacation", "visit", "itinerary"]):
            return "travel"
        
        elif any(word in query_lower for word in ["alert", "monitor", "notify", "warning", "track"]):
            return "alerts"
            
        elif any(word in query_lower for word in ["compare sources", "accurate", "reliable", "consensus", "multiple sources"]):
            return "intelligence"
            
        else:
            return "weather"  # Default to existing weather agent
    
    async def _route_to_travel_agent(self, query: str) -> Dict[str, Any]:
        """Route to travel agent coordination - uses existing weather agent internally."""
        if not self.travel_agent:
            return {
                "success": False,
                "error": "Travel agent not available - install langchain dependencies",
                "coordination_type": "travel_unavailable"
            }
        
        result = await self.travel_agent.plan_travel_with_weather(query)
        result["coordination_type"] = "travel_weather"
        return result
    
    async def _route_to_alert_agent(self, query: str) -> Dict[str, Any]:
        """Route to alert agent coordination."""
        
        # For demo, setup alerts based on query
        if "setup" in query.lower() or "monitor" in query.lower():
            # Extract locations from query using existing location extraction
            locations = await self._extract_locations_from_query(query)
            
            config = {
                "locations": locations or ["San Francisco"],  # Default
                "alert_types": ["severe_weather", "temperature_extreme"],
                "thresholds": {"temperature_high": 85, "temperature_low": 35},
                "notifications": {"email": True}
            }
            
            result = await self.alert_agent.setup_smart_alerts(config)
            result["coordination_type"] = "alert_setup"
            return result
        
        else:
            # Check existing alerts
            alerts = await self.alert_agent.check_alerts_for_all_subscriptions()
            return {
                "success": True,
                "alerts": alerts,
                "message": f"Found {len(alerts)} active alerts",
                "coordination_type": "alert_check"
            }
    
    async def _route_to_intelligence_agent(self, query: str) -> Dict[str, Any]:
        """Route to intelligence agent coordination."""
        
        locations = await self._extract_locations_from_query(query)
        location = locations[0] if locations else "San Francisco"
        
        result = await self.intelligence_agent.get_consensus_weather(location)
        result["coordination_type"] = "multi_source_intelligence"
        return result
    
    async def _route_to_weather_agent(self, query: str) -> Dict[str, Any]:
        """Route to existing weather agent (no changes needed)."""
        # Always use simple orchestrator if weather_orchestrator fails or unavailable
        if self.weather_orchestrator:
            try:
                result = await self.weather_orchestrator.process_query(query)
                # Check if the result indicates a model error
                if not result.get("success", True) and "model" in result.get("error", "").lower():
                    print("⚠️ Weather orchestrator failed, falling back to simple orchestrator")
                    result = await self.simple_orchestrator.process_query(query)
                    result["coordination_type"] = "simple_weather_agent"
                else:
                    result["coordination_type"] = "single_weather_agent"
            except Exception as e:
                print(f"⚠️ Weather orchestrator exception: {e}, falling back to simple orchestrator")
                result = await self.simple_orchestrator.process_query(query)
                result["coordination_type"] = "simple_weather_agent"
        else:
            # Fallback to simple orchestrator
            result = await self.simple_orchestrator.process_query(query)
            result["coordination_type"] = "simple_weather_agent"
        return result
    
    async def _extract_locations_from_query(self, query: str) -> List[str]:
        """Reuse existing location extraction logic with minimal changes."""
        
        # Use simple orchestrator for location extraction
        locations = self.simple_orchestrator._extract_locations(query)
        return locations


# MINIMAL CHANGES TO YOUR EXISTING main.py
class EnhancedAgenticMCPClient(AgenticMCPClient):
    """
    Enhanced version of your existing MCP client with agent coordination.
    Minimal changes - just adds coordination capability.
    """
    
    def __init__(self):
        super().__init__()
        self.coordination_hub = AgentCoordinationHub()
    
    async def process_query_with_coordination(self, query: str, verbose: bool = False) -> Dict[str, Any]:
        """
        Enhanced version of your existing process_query method.
        Now supports agent-to-agent coordination with minimal changes.
        """
        
        print(f"\n🤖 Enhanced Processing: '{query}'")
        print("🔄 Checking for agent coordination opportunities...")
        
        start_time = datetime.now()
        
        # Use new coordination hub (this is the only major addition)
        result = await self.coordination_hub.process_coordinated_query(query)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        if result["success"]:
            coordination_type = result.get("coordination_type", "single_agent")
            print(f"\n✅ Query processed using {coordination_type} in {execution_time:.2f}s")
            
            # Display results based on coordination type
            if coordination_type == "travel_weather":
                print(f"🧳 Travel Plan: {result.get('travel_plan', '')[:200]}...")
                if result.get('destinations'):
                    print(f"📍 Destinations: {', '.join(result['destinations'])}")
                    
            elif coordination_type == "multi_source_intelligence":
                consensus = result.get('consensus')
                if consensus:
                    print(f"🧠 Intelligence: {consensus.temperature}°F, {consensus.conditions}")
                    print(f"🎯 Confidence: {consensus.confidence_score*100:.0f}% from {consensus.source_count} sources")
                    
            elif coordination_type.startswith("alert"):
                alerts = result.get('alerts', [])
                print(f"🚨 Alerts: {len(alerts)} active alerts")
                
            else:
                # Existing weather response
                print(f"🌤️ Weather: {result.get('response', '')[:100]}...")
            
            if verbose and 'execution_log' in result:
                print(f"\n🔍 Coordination Log:")
                for i, log_entry in enumerate(result['execution_log'], 1):
                    print(f"   {i}. {log_entry}")
        else:
            print(f"\n❌ Query failed: {result.get('error', 'Unknown error')}")
        
        return result


async def demo_minimal_integration():
    """
    Demo showing how agent coordination integrates with existing code.
    This shows the MINIMAL CHANGES needed to add agent-to-agent protocols.
    """
    
    print("🚀 Minimal Integration Demo - Agent Coordination")
    print("=" * 70)
    print("This shows how to add agent-to-agent protocols with minimal code changes")
    print()
    
    # Use enhanced client (minimal change from existing AgenticMCPClient)
    client = EnhancedAgenticMCPClient()
    
    test_scenarios = [
        {
            "query": "What's the weather in London?", 
            "expected": "single weather agent (existing behavior)"
        },
        {
            "query": "Plan a trip to Paris and Rome - what's the weather like?",
            "expected": "travel + weather agent coordination"
        },
        {
            "query": "Set up weather alerts for San Francisco",
            "expected": "alert agent coordination"
        },
        {
            "query": "Get the most accurate weather for New York from multiple sources",
            "expected": "intelligence agent coordination"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📝 Scenario {i}: {scenario['expected']}")
        print(f"💬 Query: \"{scenario['query']}\"")
        print("-" * 50)
        
        result = await client.process_query_with_coordination(scenario['query'], verbose=True)
        
        print(f"🎯 Coordination Used: {result.get('coordination_used', 'unknown')}")
        
        if not result.get("success"):
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")


# SUMMARY of minimal changes needed:
INTEGRATION_SUMMARY = """
🎯 MINIMAL CHANGES NEEDED FOR AGENT-TO-AGENT PROTOCOLS:

1. ADD NEW AGENT FILES (3 new files):
   ├── travel_agent.py          (Travel planning coordination)
   ├── smart_alert_agent.py     (Proactive monitoring coordination)
   └── weather_intelligence_agent.py (Multi-source data coordination)

2. EXTEND EXISTING CLIENT (1 small change):
   └── Wrap existing AgenticMCPClient with coordination hub

3. NO CHANGES NEEDED TO:
   ├── weather.py              (existing MCP server)
   ├── agent_orchestrator.py   (existing LangGraph orchestrator) 
   ├── server_registry.py      (existing server discovery)
   └── config.py              (existing configuration)

4. COORDINATION BENEFITS:
   ├── 🧳 Travel + Weather planning
   ├── 🚨 Smart proactive alerts  
   ├── 🧠 Multi-source intelligence
   └── 🔄 Automatic agent routing

5. EXISTING LLM CALLS REUSED:
   ├── Same OllamaLLM(model="llama3") 
   ├── Same PromptTemplate patterns
   ├── Same chain.invoke() calls
   └── Same JSON response handling

This gives you agent-to-agent protocols while preserving ALL existing functionality!
"""

if __name__ == "__main__":
    print(INTEGRATION_SUMMARY)
    print("\n" + "="*70)
    asyncio.run(demo_minimal_integration())