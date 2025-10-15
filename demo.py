#!/usr/bin/env python3
"""
Demo Script for Agentic MCP Weather System

This script demonstrates the key capabilities of the agentic MCP system
including server discovery, orchestration, and intelligent query processing.
"""

import asyncio
import time
from typing import List
from datetime import datetime

from server_registry import registry
from simple_orchestrator import SimpleOrchestrator
from mcp_client import AgenticMCPClient


class SystemDemo:
    """Comprehensive demo of the agentic MCP system."""
    
    def __init__(self):
        self.client = AgenticMCPClient()
    
    def print_banner(self, title: str, char: str = "="):
        """Print a formatted banner."""
        print(f"\n{char * 60}")
        print(f"  {title}")
        print(f"{char * 60}")
    
    def print_section(self, title: str):
        """Print a section header."""
        print(f"\n🔹 {title}")
        print("-" * 40)
    
    async def demo_server_discovery(self):
        """Demonstrate server discovery and registry features."""
        self.print_banner("🔍 SERVER DISCOVERY & REGISTRY", "=")
        
        print("Initializing server registry...")
        await asyncio.sleep(1)
        
        # List all servers
        summary = await self.client.list_servers()
        
        # Show server details
        if summary["servers"]:
            server_name = summary["servers"][0]["name"]
            self.print_section(f"Server Details: {server_name}")
            await self.client.server_details(server_name)
    
    async def demo_basic_queries(self):
        """Demonstrate basic weather query processing."""
        self.print_banner("🤖 BASIC AGENTIC QUERIES", "=")
        
        basic_queries = [
            "What's the weather in London?",
            "Show me current conditions in Tokyo",
            "How's the weather in Paris today?",
        ]
        
        for query in basic_queries:
            self.print_section(f"Query: {query}")
            result = await self.client.process_query(query, verbose=False)
            await asyncio.sleep(1)
    
    async def demo_advanced_queries(self):
        """Demonstrate advanced multi-location and complex queries."""
        self.print_banner("🧠 ADVANCED AGENTIC CAPABILITIES", "=")
        
        advanced_queries = [
            "Compare weather in New York and Los Angeles",
            "What's the forecast for Berlin tomorrow?",
            "Any weather alerts in California?",
            "Show me weather conditions in London, Paris, and Tokyo",
        ]
        
        for query in advanced_queries:
            self.print_section(f"Complex Query: {query}")
            result = await self.client.process_query(query, verbose=True)
            await asyncio.sleep(2)
    
    async def demo_orchestration_intelligence(self):
        """Demonstrate the orchestrator's intelligence and task classification."""
        self.print_banner("⚡ ORCHESTRATION INTELLIGENCE", "=")
        
        orchestrator = SimpleOrchestrator()
        
        test_cases = [
            {
                "query": "What's the weather like in Seattle?",
                "expected_type": "weather_query",
                "expected_locations": ["Seattle"]
            },
            {
                "query": "Compare weather in Miami and Chicago",
                "expected_type": "multi_location", 
                "expected_locations": ["Miami", "Chicago"]
            },
            {
                "query": "Any storms coming to Texas?",
                "expected_type": "alert_monitoring",
                "expected_locations": ["Texas"]
            },
            {
                "query": "What's the forecast for tomorrow in Boston?",
                "expected_type": "forecast_analysis",
                "expected_locations": ["Boston"]
            }
        ]
        
        print("🧪 Testing Task Classification & Location Extraction:")
        print()
        
        for i, case in enumerate(test_cases, 1):
            # Classify task
            task_type = orchestrator._classify_task(case["query"])
            locations = orchestrator._extract_locations(case["query"])
            
            print(f"Test {i}: {case['query']}")
            print(f"   📋 Task Type: {task_type.value}")
            print(f"   📍 Locations: {locations}")
            print(f"   ✅ Classification: {'✓' if task_type.value == case['expected_type'] else '✗'}")
            print(f"   🎯 Location Match: {'✓' if set(locations) >= set(case['expected_locations']) else '✗'}")
            print()
    
    async def demo_error_handling(self):
        """Demonstrate error handling and resilience."""
        self.print_banner("🛡️ ERROR HANDLING & RESILIENCE", "=")
        
        error_scenarios = [
            "What's the weather in NonexistentCity12345?",
            "Show me weather in XYZ location that doesn't exist",
            "",  # Empty query
            "Random unrelated question about cooking",
        ]
        
        for query in error_scenarios:
            if not query:
                query = "[Empty Query]"
                actual_query = ""
            else:
                actual_query = query
                
            self.print_section(f"Error Scenario: {query}")
            result = await self.client.process_query(actual_query, verbose=False)
            await asyncio.sleep(1)
    
    async def demo_performance_metrics(self):
        """Demonstrate performance monitoring and metrics."""
        self.print_banner("📊 PERFORMANCE & METRICS", "=")
        
        print("🚀 Performance Testing:")
        print()
        
        test_queries = [
            "Weather in London",
            "Compare New York and Paris weather",
            "Forecast for Tokyo",
        ]
        
        total_times = []
        
        for query in test_queries:
            start_time = time.time()
            result = await self.client.process_query(query, verbose=False)
            end_time = time.time()
            
            execution_time = end_time - start_time
            total_times.append(execution_time)
            
            print(f"⏱️  '{query}': {execution_time:.2f}s")
        
        print(f"\n📈 Performance Summary:")
        print(f"   Average Response Time: {sum(total_times)/len(total_times):.2f}s")
        print(f"   Fastest Query: {min(total_times):.2f}s") 
        print(f"   Slowest Query: {max(total_times):.2f}s")
    
    async def demo_system_status(self):
        """Show comprehensive system status."""
        self.print_banner("📊 SYSTEM STATUS OVERVIEW", "=")
        
        await self.client._show_system_status()
    
    async def run_full_demo(self):
        """Run the complete demonstration."""
        print("🌟 AGENTIC MCP WEATHER SYSTEM DEMONSTRATION")
        print("=" * 60)
        print("This demo showcases the key capabilities of our agentic MCP system")
        print("including intelligent orchestration, server discovery, and natural")
        print("language query processing.")
        print()
        
        input("Press Enter to start the demonstration...")
        
        # Run all demo sections
        await self.demo_server_discovery()
        input("\nPress Enter to continue to basic queries...")
        
        await self.demo_basic_queries()
        input("\nPress Enter to continue to advanced capabilities...")
        
        await self.demo_advanced_queries()
        input("\nPress Enter to see orchestration intelligence...")
        
        await self.demo_orchestration_intelligence()
        input("\nPress Enter to see error handling...")
        
        await self.demo_error_handling()
        input("\nPress Enter to see performance metrics...")
        
        await self.demo_performance_metrics()
        input("\nPress Enter to see final system status...")
        
        await self.demo_system_status()
        
        self.print_banner("✨ DEMONSTRATION COMPLETE", "=")
        print("🎉 Thank you for exploring the Agentic MCP Weather System!")
        print()
        print("Next steps:")
        print("1. Try the interactive mode: uv run mcp_client.py")
        print("2. Explore the codebase and extend with new servers")
        print("3. Build your own agentic applications using this framework")
        print()
        print("Happy building! 🚀")


async def main():
    """Main demo function."""
    demo = SystemDemo()
    
    # Check if we should run full demo or quick demo
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Quick demo
        await demo.demo_server_discovery()
        await demo.demo_basic_queries()
        await demo.demo_orchestration_intelligence()
    else:
        # Full interactive demo
        await demo.run_full_demo()


if __name__ == "__main__":
    asyncio.run(main())