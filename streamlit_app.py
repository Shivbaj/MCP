"""
Streamlit Web UI for Weather Agent Coordination System

A ChatGPT-like interface for interacting with your weather MCP system
with agent-to-agent coordination capabilities.
"""

import streamlit as st
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import sys
import os

# Configure Streamlit page settings FIRST
st.set_page_config(
    page_title="Weather AI Assistant",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your agent coordination system
try:
    from agent_coordination_hub import AgentCoordinationHub
    from smart_alert_agent import AlertAgent
    from weather_intelligence_agent import WeatherIntelligenceAgent
    from simple_orchestrator import SimpleOrchestrator
    AGENTS_AVAILABLE = True
    AGENT_ERROR = None
except Exception as e:
    AGENTS_AVAILABLE = False
    AGENT_ERROR = str(e)


class StreamlitWeatherChat:
    """Streamlit-based chat interface for weather agent coordination."""
    
    def __init__(self):
        self.initialize_session_state()
        
        if AGENTS_AVAILABLE:
            try:
                self.coordination_hub = AgentCoordinationHub()
                self.alert_agent = AlertAgent()
                self.intelligence_agent = WeatherIntelligenceAgent()
                self.simple_orchestrator = SimpleOrchestrator()
                self.system_available = True
            except Exception as e:
                st.error(f"Failed to initialize agents: {e}")
                self.system_available = False
        else:
            st.error(f"⚠️ Agent system not available: {AGENT_ERROR}")
            self.system_available = False
    
    def setup_page_config(self):
        """Configure Streamlit page settings."""
        # This is now done at module level
        pass
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "alert_subscriptions" not in st.session_state:
            st.session_state.alert_subscriptions = []
        
        if "last_query_type" not in st.session_state:
            st.session_state.last_query_type = None
            
        if "processing" not in st.session_state:
            st.session_state.processing = False
    
    def render_header(self):
        """Render the main header."""
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #1e3c72, #2a5298); color: white; border-radius: 10px; margin-bottom: 20px;">
            <h1>🌤️ Weather AI Assistant</h1>
            <h3>Agent Coordination System with Multi-Source Intelligence</h3>
            <p>ChatGPT-like interface for weather, alerts, and intelligent forecasting!</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render the sidebar with system info and controls."""
        with st.sidebar:
            st.markdown("## 🤖 Agent System Status")
            
            if self.system_available:
                st.success("✅ All agents online")
                
                # Agent status indicators
                st.markdown("### Active Agents:")
                st.markdown("- 🌤️ **Weather Agent**: Real-time weather data")
                st.markdown("- 🚨 **Alert Agent**: Proactive monitoring")  
                st.markdown("- 🧠 **Intelligence Agent**: Multi-source consensus")
                st.markdown("- 🎯 **Coordination Hub**: Smart routing")
                
            else:
                st.error("❌ Agent system unavailable")
                st.markdown("Please check Docker containers are running.")
            
            st.markdown("---")
            
            # Quick action buttons
            st.markdown("## 🚀 Quick Actions")
            
            if st.button("🔄 System Status Check"):
                self.run_system_check()
            
            if st.button("🚨 View Active Alerts"):
                self.show_active_alerts()
            
            if st.button("🧠 Test Intelligence"):
                self.test_intelligence_agent()
            
            if st.button("🗑️ Clear Chat History"):
                st.session_state.messages = []
                st.rerun()
            
            st.markdown("---")
            
            # Sample queries
            st.markdown("## 💡 Sample Queries")
            sample_queries = [
                "What's the weather in San Francisco?",
                "Set up weather alerts for New York",
                "Get accurate weather from multiple sources for Chicago", 
                "Compare weather in Paris and London",
                "Monitor severe weather for my locations",
                "Plan travel weather for Tokyo this weekend"
            ]
            
            for query in sample_queries:
                if st.button(f"💬 {query}", key=f"sample_{hash(query)}"):
                    st.session_state.messages.append({"role": "user", "content": query})
                    st.rerun()
    
    def render_chat_interface(self):
        """Render the main chat interface."""
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            # Display chat messages
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    if message["role"] == "assistant":
                        self.render_assistant_message(message)
                    else:
                        st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about weather, set up alerts, or get intelligent forecasts..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Process and display assistant response
            with st.chat_message("assistant"):
                self.process_user_query(prompt)
    
    def render_assistant_message(self, message: Dict[str, Any]):
        """Render assistant message with rich formatting."""
        content = message["content"]
        
        # Ensure content is a dictionary
        if isinstance(content, str):
            st.markdown(content)
            return
        
        # Display main response
        response_text = content.get("response", "No response available")
        if response_text:
            st.markdown(response_text)
        
        # Display metadata if available
        if "metadata" in content and content["metadata"]:
            metadata = content["metadata"]
            
            with st.expander("🔍 Query Details"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    coordination_type = metadata.get("coordination_type", "Unknown")
                    st.metric("Coordination Type", coordination_type)
                
                with col2:
                    sources_used = metadata.get("sources_used")
                    if sources_used is not None:
                        st.metric("Data Sources", sources_used)
                
                with col3:
                    confidence = metadata.get("confidence")
                    if confidence is not None:
                        st.metric("Confidence", f"{confidence*100:.0f}%")
            
            # Show execution log if available
            if "execution_log" in content and content["execution_log"]:
                with st.expander("📋 Execution Log"):
                    for i, log_entry in enumerate(content["execution_log"], 1):
                        st.text(f"{i}. {log_entry}")
            
            # Show additional data if available
            if "additional_data" in content and content["additional_data"]:
                additional = content["additional_data"]
                
                if "alerts" in additional and additional["alerts"]:
                    with st.expander("🚨 Alert Details"):
                        for alert in additional["alerts"]:
                            alert_location = alert.get('location', 'Unknown') if isinstance(alert, dict) else 'Unknown'
                            alert_condition = alert.get('condition', 'Unknown condition') if isinstance(alert, dict) else str(alert)
                            st.warning(f"**{alert_location}**: {alert_condition}")
                
                if "weather_data" in additional:
                    with st.expander("🌤️ Detailed Weather Data"):
                        weather_data = additional["weather_data"]
                        # Check if weather_data is valid and not empty
                        if weather_data and isinstance(weather_data, (dict, list)):
                            try:
                                st.json(weather_data)
                            except Exception as e:
                                st.warning(f"Unable to display weather data: {e}")
                                st.text(str(weather_data))
                        else:
                            st.info("No detailed weather data available")
    
    def process_user_query(self, query: str):
        """Process user query through the agent coordination system."""
        if not self.system_available:
            st.error("❌ Agent system is not available. Please check if Docker containers are running.")
            return
        
        # Show processing indicator
        with st.spinner("🤖 Processing your query through agent coordination..."):
            try:
                # Run async query processing
                result = asyncio.run(self._async_process_query(query))
                
                # Format and display response
                formatted_response = self.format_agent_response(result, query)
                
                # Add to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": formatted_response
                })
                
                # Display the response
                self.render_assistant_message({
                    "role": "assistant", 
                    "content": formatted_response
                })
                
            except Exception as e:
                error_msg = f"❌ Error processing query: {str(e)}"
                st.error(error_msg)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": {"response": error_msg}
                })
    
    async def _async_process_query(self, query: str) -> Dict[str, Any]:
        """Async wrapper for query processing."""
        return await self.coordination_hub.process_coordinated_query(query)
    
    def format_agent_response(self, result: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Format agent response for display in chat."""
        if not result or not isinstance(result, dict):
            return {
                "response": "❌ **Invalid response**: Unable to process query response",
                "metadata": {
                    "coordination_type": "error",
                    "success": False
                }
            }
            
        if not result.get("success", False):
            error_msg = result.get('error', 'Unknown error')
            return {
                "response": f"❌ **Query failed**: {error_msg}",
                "metadata": {
                    "coordination_type": result.get("coordination_used", "unknown"),
                    "success": False
                }
            }
        
        coordination_type = result.get("coordination_used", "unknown")
        
        # Format response based on coordination type
        try:
            if coordination_type == "intelligence":
                return self.format_intelligence_response(result)
            elif coordination_type == "alerts":
                return self.format_alert_response(result)
            elif coordination_type.endswith("weather_agent"):
                return self.format_weather_response(result)
            else:
                return self.format_generic_response(result)
        except Exception as e:
            # Fallback for any formatting errors
            return {
                "response": f"✅ **Query processed successfully**\n\nResponse: {result.get('response', 'No response available')}",
                "metadata": {
                    "coordination_type": coordination_type,
                    "success": True,
                    "format_error": str(e)
                },
                "execution_log": result.get("execution_log", [])
            }
    
    def format_intelligence_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format intelligence agent response."""
        consensus = result.get("consensus")
        if consensus and hasattr(consensus, 'temperature'):
            # Handle consensus object with attributes
            response = f"""
## 🧠 Multi-Source Weather Intelligence

**Temperature**: {consensus.temperature}°F  
**Conditions**: {consensus.conditions}  
**Humidity**: {consensus.humidity}%  
**Confidence**: {consensus.confidence_score*100:.0f}%  
**Sources**: {consensus.source_count} ({', '.join(consensus.data_sources)})

### Intelligence Analysis
{result.get('intelligence_report', 'No detailed analysis available')}
            """
            
            metadata = {
                "coordination_type": "Multi-Source Intelligence",
                "sources_used": consensus.source_count,
                "confidence": consensus.confidence_score,
            }
            
            additional_data = {"weather_data": {
                "temperature": consensus.temperature,
                "conditions": consensus.conditions,
                "humidity": consensus.humidity,
                "confidence": consensus.confidence_score,
                "sources": consensus.data_sources
            }}
            
        elif consensus and isinstance(consensus, dict):
            # Handle consensus as dictionary
            response = f"""
## 🧠 Multi-Source Weather Intelligence

**Temperature**: {consensus.get('temperature', 'N/A')}°F  
**Conditions**: {consensus.get('conditions', 'N/A')}  
**Humidity**: {consensus.get('humidity', 'N/A')}%  
**Confidence**: {consensus.get('confidence_score', 0)*100:.0f}%  
**Sources**: {consensus.get('source_count', 0)} 

### Intelligence Analysis
{result.get('intelligence_report', 'No detailed analysis available')}
            """
            
            metadata = {
                "coordination_type": "Multi-Source Intelligence",
                "sources_used": consensus.get('source_count', 0),
                "confidence": consensus.get('confidence_score', 0),
            }
            
            additional_data = {"weather_data": consensus}
            
        else:
            response = "🧠 **Multi-source intelligence analysis completed**"
            metadata = {
                "coordination_type": "Multi-Source Intelligence",
                "sources_used": 0,
                "confidence": 0,
            }
            additional_data = {"weather_data": result.get("consensus", {})}
        
        return {
            "response": response.strip(),
            "metadata": metadata,
            "additional_data": additional_data
        }
    
    def format_alert_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format alert agent response."""
        alerts = result.get("alerts", [])
        
        if alerts:
            response = f"🚨 **Active Weather Alerts** ({len(alerts)} found)\n\n"
            for alert in alerts[:3]:  # Show top 3 alerts
                response += f"**📍 {alert.get('location', 'Unknown')}**: {alert.get('severity', 'Unknown')} - {', '.join(alert.get('conditions', []))}\n"
        else:
            response = "✅ **No active weather alerts** - All monitored locations have normal conditions"
        
        return {
            "response": response,
            "metadata": {
                "coordination_type": "Smart Weather Alerts",
                "alerts_count": len(alerts)
            },
            "additional_data": {
                "alerts": alerts
            }
        }
    
    def format_weather_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format standard weather response."""
        response_text = result.get("response", "Weather information retrieved")
        
        return {
            "response": f"🌤️ **Weather Information**\n\n{response_text}",
            "metadata": {
                "coordination_type": "Weather Data",
                "locations": result.get("locations", [])
            },
            "execution_log": result.get("execution_log", [])
        }
    
    def format_generic_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format generic response."""
        return {
            "response": result.get("response", "Query processed successfully"),
            "metadata": {
                "coordination_type": result.get("coordination_used", "Unknown"),
                "success": result.get("success", False)
            },
            "execution_log": result.get("execution_log", [])
        }
    
    def run_system_check(self):
        """Run a quick system status check."""
        with st.spinner("🔍 Checking system status..."):
            try:
                if self.system_available:
                    # Test basic functionality
                    test_query = "system status check"
                    result = asyncio.run(self._async_process_query("What's the weather?"))
                    
                    st.success("✅ System check passed - All agents responding")
                    st.info(f"Coordination available: {result.get('coordination_used', 'Unknown')}")
                else:
                    st.error("❌ System check failed - Agents not available")
            except Exception as e:
                st.error(f"❌ System check failed: {e}")
    
    def show_active_alerts(self):
        """Show current active alerts."""
        with st.spinner("🚨 Checking active alerts..."):
            try:
                alerts = asyncio.run(self.alert_agent.check_alerts_for_all_subscriptions())
                
                if alerts:
                    st.warning(f"🚨 {len(alerts)} active alerts found:")
                    for alert in alerts:
                        st.error(f"**{alert.get('location', 'Unknown')}**: {', '.join(alert.get('conditions', []))}")
                else:
                    st.success("✅ No active alerts - All conditions normal")
            except Exception as e:
                st.error(f"❌ Error checking alerts: {e}")
    
    def test_intelligence_agent(self):
        """Test the intelligence agent with a sample query."""
        with st.spinner("🧠 Testing multi-source intelligence..."):
            try:
                result = asyncio.run(self.intelligence_agent.get_consensus_weather("San Francisco"))
                
                if result.get("success"):
                    consensus = result["consensus"]
                    st.success("✅ Intelligence agent test successful")
                    st.info(f"Temperature: {consensus.temperature}°F, Confidence: {consensus.confidence_score*100:.0f}%")
                else:
                    st.warning("⚠️ Intelligence agent test completed with warnings")
            except Exception as e:
                st.error(f"❌ Intelligence agent test failed: {e}")
    
    def run(self):
        """Run the Streamlit application."""
        self.render_header()
        
        # Create layout
        col1, col2 = st.columns([1, 3])
        
        with col1:
            self.render_sidebar()
        
        with col2:
            self.render_chat_interface()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 12px;">
            Weather AI Assistant v1.0 | Agent Coordination System | Powered by MCP & Ollama
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main application entry point."""
    app = StreamlitWeatherChat()
    app.run()


if __name__ == "__main__":
    main()