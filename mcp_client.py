"""
Enhanced MCP Client with Agentic Orchestrator

This module provides an advanced MCP client that uses LangGraph orchestration
to handle complex agentic workflows with multiple MCP servers.
"""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime

from server_registry import registry, MCPServerRegistry
from simple_orchestrator import SimpleOrchestrator


class AgenticMCPClient:
    """Advanced MCP client with agentic capabilities."""
    
    def __init__(self):
        self.registry = registry
        self.orchestrator = SimpleOrchestrator()
    
    async def list_servers(self) -> Dict[str, Any]:
        """List all available MCP servers with their status."""
        print("🔍 Discovering MCP servers...")
        
        # Check health of all servers
        health_results = await self.registry.health_check_all()
        
        summary = self.registry.get_servers_summary()
        
        print(f"📊 Found {summary['total_servers']} registered servers:")
        print(f"   ✅ Online: {summary['online']}")
        print(f"   ❌ Offline: {summary['offline']}")
        print(f"   ⚠️  Error: {summary['error']}")
        print(f"   ❓ Unknown: {summary['unknown']}")
        
        return summary
    
    async def server_details(self, server_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific server."""
        server = self.registry.get_server(server_name)
        if not server:
            print(f"❌ Server '{server_name}' not found")
            return None
        
        print(f"\n📋 Server Details: {server.name}")
        print(f"   🌐 URL: {server.base_url}")
        print(f"   📝 Description: {server.description}")
        print(f"   🔧 Tools: {', '.join(server.tools)}")
        print(f"   🏷️  Tags: {', '.join(server.tags)}")
        print(f"   📡 Status: {server.status.value}")
        print(f"   ⏰ Last Check: {server.last_check}")
        
        return server.to_dict()
    
    async def process_query(self, query: str, verbose: bool = False) -> Dict[str, Any]:
        """Process a natural language query using the orchestrator."""
        print(f"\n🤖 Processing query: '{query}'")
        print("⚡ Activating agentic workflow...")
        
        start_time = datetime.now()
        result = await self.orchestrator.process_query(query)
        end_time = datetime.now()
        
        execution_time = (end_time - start_time).total_seconds()
        
        if result["success"]:
            print(f"\n✅ Query processed successfully in {execution_time:.2f}s")
            print(f"🎯 Task Type: {result['task_type']}")
            if result['locations']:
                print(f"📍 Locations: {', '.join(result['locations'])}")
            
            print(f"\n🤖 Agent Response:")
            print(f"   {result['response']}")
            
            if verbose:
                print(f"\n🔍 Execution Log:")
                for i, log_entry in enumerate(result['execution_log'], 1):
                    print(f"   {i}. {log_entry}")
        else:
            print(f"\n❌ Query failed: {result['error']}")
        
        return result
    
    async def interactive_mode(self):
        """Start an interactive session with the MCP client."""
        print("🚀 Welcome to the Agentic MCP Client!")
        print("Type 'help' for commands, 'quit' to exit")
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                elif user_input.lower() == 'servers':
                    await self.list_servers()
                elif user_input.lower().startswith('server '):
                    server_name = user_input[7:].strip()
                    await self.server_details(server_name)
                elif user_input.lower() == 'status':
                    await self._show_system_status()
                elif user_input:
                    await self.process_query(user_input, verbose=True)
                else:
                    print("❓ Please enter a query or command")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    def _show_help(self):
        """Show help information."""
        print("\n📚 Available Commands:")
        print("   help          - Show this help message")
        print("   servers       - List all registered MCP servers")
        print("   server <name> - Show details for a specific server")
        print("   status        - Show system status")
        print("   quit/exit/q   - Exit the client")
        print("\n🤖 Or just ask any weather-related question!")
        print("   Examples:")
        print("   - 'What's the weather in London?'")
        print("   - 'Compare weather in New York and Paris'")
        print("   - 'Any alerts in California?'")
        print("   - 'Show me the forecast for tomorrow'")
    
    async def _show_system_status(self):
        """Show overall system status."""
        print("\n📊 System Status:")
        
        # Registry status
        summary = await self.list_servers()
        
        # Orchestrator status
        print(f"\n🤖 Orchestrator: Ready")
        print(f"   🧠 Processing: Rule-based + Pattern matching")
        print(f"   🔄 Workflow: Simplified agentic workflow")
        
        # Available capabilities
        print(f"\n🛠️  Available Capabilities:")
        print(f"   🌤️  Weather queries")
        print(f"   📅 Forecast analysis")  
        print(f"   🚨 Alert monitoring")
        print(f"   🗺️  Multi-location comparison")


async def main():
    """Main function with example usage."""
    client = AgenticMCPClient()
    
    print("🌟 Agentic MCP Client Demo")
    print("=" * 50)
    
    # Show available servers
    await client.list_servers()
    
    # Example queries
    example_queries = [
        "What's the weather like in London?",
        "Any weather alerts in New York?",
    ]
    
    for query in example_queries:
        await client.process_query(query)
    
    # Start interactive mode
    print("\n🔄 Starting interactive mode...")
    await client.interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())
