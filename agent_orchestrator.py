"""
LangGraph Orchestrator for Agentic MCP Applications

This module provides a LangGraph-based orchestrator that can coordinate
multiple MCP servers to handle complex agentic workflows.
"""

from typing import Dict, List, Any, Optional, TypedDict, Annotated
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
import asyncio
import httpx
import json
from datetime import datetime
from enum import Enum

from server_registry import MCPServerRegistry, MCPServer, registry


class TaskType(Enum):
    """Types of tasks the orchestrator can handle."""
    WEATHER_QUERY = "weather_query"
    FORECAST_ANALYSIS = "forecast_analysis" 
    ALERT_MONITORING = "alert_monitoring"
    MULTI_LOCATION = "multi_location"
    GENERAL_INQUIRY = "general_inquiry"


class AgentState(TypedDict):
    """State that gets passed between nodes in the graph."""
    messages: List[str]
    user_query: str
    task_type: TaskType
    locations: List[str]
    weather_data: Dict[str, Any]
    forecast_data: Dict[str, Any]
    alert_data: Dict[str, Any]
    analysis_result: str
    error_messages: List[str]
    execution_log: List[str]
    metadata: Dict[str, Any]


class MCPToolCaller:
    """Handles calling MCP server tools."""
    
    def __init__(self, registry: MCPServerRegistry):
        self.registry = registry
    
    async def call_weather_tool(self, city: str) -> Dict[str, Any]:
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
                return response.json()
        except Exception as e:
            return {"error": f"Failed to call weather tool: {str(e)}"}
    
    async def call_forecast_tool(self, latitude: float, longitude: float) -> Dict[str, Any]:
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
                return response.json()
        except Exception as e:
            return {"error": f"Failed to call forecast tool: {str(e)}"}
    
    async def call_alerts_tool(self, state: str) -> Dict[str, Any]:
        """Call the alerts tool on the weather server."""
        server = self.registry.get_server("weather-server")
        if not server:
            return {"error": "Weather server not found"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{server.base_url}/tools/get_alerts",
                    json={"state": state},
                    timeout=10.0
                )
                return response.json()
        except Exception as e:
            return {"error": f"Failed to call alerts tool: {str(e)}"}


class WeatherOrchestrator:
    """LangGraph-based orchestrator for weather-related agentic workflows."""
    
    def __init__(self, llm_model: str = "llama3"):
        self.llm = OllamaLLM(model=llm_model)
        self.registry = registry
        self.tool_caller = MCPToolCaller(self.registry)
        self.graph = self._build_graph()
    
    def _classify_task(self, state: AgentState) -> AgentState:
        """Classify the user query to determine task type."""
        query = state["user_query"].lower()
        
        if any(word in query for word in ["forecast", "prediction", "future", "tomorrow", "week"]):
            state["task_type"] = TaskType.FORECAST_ANALYSIS
        elif any(word in query for word in ["alert", "warning", "storm", "emergency"]):
            state["task_type"] = TaskType.ALERT_MONITORING
        elif any(word in query for word in ["multiple", "compare", "cities", "locations"]):
            state["task_type"] = TaskType.MULTI_LOCATION
        elif any(word in query for word in ["weather", "temperature", "current", "now"]):
            state["task_type"] = TaskType.WEATHER_QUERY
        else:
            state["task_type"] = TaskType.GENERAL_INQUIRY
        
        state["execution_log"].append(f"Task classified as: {state['task_type'].value}")
        return state
    
    def _extract_locations(self, state: AgentState) -> AgentState:
        """Extract location information from the query."""
        # Simple location extraction - in production, use NER or geocoding
        query = state["user_query"]
        
        # Use LLM to extract locations
        template = """
        Extract location names (cities, states, countries) from this query: {query}
        
        Return only a comma-separated list of location names, nothing else.
        If no locations found, return "none".
        
        Examples:
        - "Weather in London" -> "London"
        - "Compare weather in New York and Paris" -> "New York, Paris"
        - "What's the temperature?" -> "none"
        """
        
        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm
        
        result = chain.invoke({"query": query}).strip()
        
        if result.lower() != "none":
            locations = [loc.strip() for loc in result.split(",")]
            state["locations"] = locations
        else:
            state["locations"] = []
        
        state["execution_log"].append(f"Extracted locations: {state['locations']}")
        return state
    
    async def _gather_weather_data(self, state: AgentState) -> AgentState:
        """Gather weather data for the identified locations."""
        weather_data = {}
        
        for location in state["locations"]:
            data = await self.tool_caller.call_weather_tool(location)
            weather_data[location] = data
            
        state["weather_data"] = weather_data
        state["execution_log"].append(f"Gathered weather data for {len(state['locations'])} locations")
        return state
    
    async def _gather_forecast_data(self, state: AgentState) -> AgentState:
        """Gather forecast data (requires coordinates - simplified for demo)."""
        # For demo, using default coordinates for first location
        if state["locations"]:
            # London coordinates as example
            data = await self.tool_caller.call_forecast_tool(51.5074, -0.1278)
            state["forecast_data"] = {state["locations"][0]: data}
            state["execution_log"].append("Gathered forecast data")
        
        return state
    
    async def _gather_alert_data(self, state: AgentState) -> AgentState:
        """Gather alert data for US states."""
        alert_data = {}
        
        # Extract US state codes from locations (simplified)
        us_states = {"CA", "NY", "TX", "FL", "WA"}  # Add more as needed
        
        for location in state["locations"]:
            # Simple mapping - in production, use proper geocoding
            if location.upper() in us_states:
                data = await self.tool_caller.call_alerts_tool(location.upper())
                alert_data[location] = data
        
        state["alert_data"] = alert_data
        state["execution_log"].append(f"Gathered alert data for {len(alert_data)} states")
        return state
    
    def _analyze_and_respond(self, state: AgentState) -> AgentState:
        """Use LLM to analyze gathered data and provide response."""
        
        context_data = {
            "weather": state.get("weather_data", {}),
            "forecast": state.get("forecast_data", {}),
            "alerts": state.get("alert_data", {})
        }
        
        template = """
        You are an intelligent weather assistant. Analyze the following data and provide a helpful, comprehensive response to the user's query.
        
        User Query: {query}
        Task Type: {task_type}
        Locations: {locations}
        
        Weather Data: {weather_data}
        Forecast Data: {forecast_data}
        Alert Data: {alert_data}
        
        Provide a natural, conversational response that directly answers the user's question.
        Include relevant details but keep it concise and actionable.
        """
        
        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm
        
        result = chain.invoke({
            "query": state["user_query"],
            "task_type": state["task_type"].value,
            "locations": state["locations"],
            "weather_data": json.dumps(context_data["weather"], indent=2),
            "forecast_data": json.dumps(context_data["forecast"], indent=2),
            "alert_data": json.dumps(context_data["alert"], indent=2)
        })
        
        state["analysis_result"] = result
        state["execution_log"].append("Analysis completed")
        return state
    
    def _route_after_classification(self, state: AgentState) -> str:
        """Route to appropriate node based on task type."""
        if state["task_type"] in [TaskType.WEATHER_QUERY, TaskType.MULTI_LOCATION]:
            return "extract_locations"
        elif state["task_type"] == TaskType.FORECAST_ANALYSIS:
            return "extract_locations"
        elif state["task_type"] == TaskType.ALERT_MONITORING:
            return "extract_locations"
        else:
            return "analyze"
    
    def _route_after_locations(self, state: AgentState) -> str:
        """Route based on task type after location extraction."""
        if state["task_type"] in [TaskType.WEATHER_QUERY, TaskType.MULTI_LOCATION]:
            return "gather_weather"
        elif state["task_type"] == TaskType.FORECAST_ANALYSIS:
            return "gather_forecast"
        elif state["task_type"] == TaskType.ALERT_MONITORING:
            return "gather_alerts"
        else:
            return "analyze"
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify", self._classify_task)
        workflow.add_node("extract_locations", self._extract_locations)
        workflow.add_node("gather_weather", self._gather_weather_data)
        workflow.add_node("gather_forecast", self._gather_forecast_data)
        workflow.add_node("gather_alerts", self._gather_alert_data)
        workflow.add_node("analyze", self._analyze_and_respond)
        
        # Add edges
        workflow.set_entry_point("classify")
        
        workflow.add_conditional_edges(
            "classify",
            self._route_after_classification,
            {
                "extract_locations": "extract_locations",
                "analyze": "analyze"
            }
        )
        
        workflow.add_conditional_edges(
            "extract_locations",
            self._route_after_locations,
            {
                "gather_weather": "gather_weather",
                "gather_forecast": "gather_forecast", 
                "gather_alerts": "gather_alerts",
                "analyze": "analyze"
            }
        )
        
        workflow.add_edge("gather_weather", "analyze")
        workflow.add_edge("gather_forecast", "analyze")
        workflow.add_edge("gather_alerts", "analyze")
        workflow.add_edge("analyze", END)
        
        return workflow.compile()
    
    async def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process a user query through the orchestrator."""
        
        initial_state = AgentState(
            messages=[],
            user_query=user_query,
            task_type=TaskType.GENERAL_INQUIRY,
            locations=[],
            weather_data={},
            forecast_data={},
            alert_data={},
            analysis_result="",
            error_messages=[],
            execution_log=[],
            metadata={"timestamp": datetime.now().isoformat()}
        )
        
        try:
            # Execute the graph
            result = await self._run_graph_async(initial_state)
            
            return {
                "success": True,
                "response": result["analysis_result"],
                "task_type": result["task_type"].value,
                "locations": result["locations"],
                "execution_log": result["execution_log"],
                "metadata": result["metadata"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_log": initial_state.get("execution_log", [])
            }
    
    async def _run_graph_async(self, initial_state: AgentState) -> AgentState:
        """Run the graph asynchronously."""
        # Since LangGraph doesn't have built-in async support for all operations,
        # we need to handle async operations manually
        
        current_state = initial_state
        
        # Classify task
        current_state = self._classify_task(current_state)
        
        # Extract locations
        if current_state["task_type"] != TaskType.GENERAL_INQUIRY:
            current_state = self._extract_locations(current_state)
        
        # Gather data based on task type
        if current_state["task_type"] in [TaskType.WEATHER_QUERY, TaskType.MULTI_LOCATION]:
            current_state = await self._gather_weather_data(current_state)
        elif current_state["task_type"] == TaskType.FORECAST_ANALYSIS:
            current_state = await self._gather_forecast_data(current_state)
        elif current_state["task_type"] == TaskType.ALERT_MONITORING:
            current_state = await self._gather_alert_data(current_state)
        
        # Analyze and respond
        current_state = self._analyze_and_respond(current_state)
        
        return current_state


async def main():
    """Example usage of the orchestrator."""
    orchestrator = WeatherOrchestrator()
    
    test_queries = [
        "What's the weather like in London?",
        "Compare weather in New York and Paris",
        "What's the forecast for tomorrow?",
        "Any weather alerts in California?",
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print(f"{'='*50}")
        
        result = await orchestrator.process_query(query)
        
        if result["success"]:
            print(f"Response: {result['response']}")
            print(f"Task Type: {result['task_type']}")
            print(f"Locations: {result['locations']}")
            print(f"Execution Log: {result['execution_log']}")
        else:
            print(f"Error: {result['error']}")


if __name__ == "__main__":
    asyncio.run(main())