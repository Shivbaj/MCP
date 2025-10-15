#!/usr/bin/env python3
"""
Production Main Entry Point for Agentic MCP Weather System

This is the primary entry point for production deployment and management.
Provides CLI interface for server management and system operations.
"""

import asyncio
import sys
import logging
from typing import List, Optional
from config import config_manager, get_logger

# Initialize logger
logger = get_logger("main")


def show_banner():
    """Display the production system banner."""
    print("🌟 PRODUCTION MCP WEATHER SYSTEM 🌟")
    print("=" * 50)
    print("Enterprise Weather Services with Multi-Server Orchestration")
    print(f"Environment: {config_manager.config.environment.value.upper()}")
    print(f"Version: {config_manager.config.version}")
    print("=" * 50)


def show_menu():
    """Display the main menu."""
    print("\n📋 Available Options:")
    print("  1. 🚀 Interactive Client Mode")
    print("  2. 🔍 Server Discovery Demo")
    print("  3. 🤖 Orchestrator Demo")
    print("  4. 📊 System Status")
    print("  5. ⚙️  Configuration")
    print("  6. 📚 Full Demo")
    print("  7. ❌ Exit")


async def run_interactive_client():
    """Run the interactive client."""
    try:
        if config_manager.is_production():
            print("⚠️  Interactive mode is disabled in production environment")
            print("   Use API endpoints directly for production usage")
            return
            
        from mcp_client import AgenticMCPClient
        
        logger.info("Starting interactive client...")
        print("\n🚀 Starting Interactive Agentic Client...")
        client = AgenticMCPClient()
        await client.interactive_mode()
        
    except Exception as e:
        logger.error(f"Failed to start interactive client: {e}")
        print(f"❌ Error: {e}")


async def run_server_discovery():
    """Demonstrate server discovery."""
    from server_registry import registry
    
    print("\n🔍 Server Discovery & Registry Demo")
    print("-" * 40)
    
    # List servers
    servers = registry.list_servers()
    print(f"📡 Registered Servers: {len(servers)}")
    
    for server in servers:
        print(f"  • {server.name} ({server.base_url})")
        print(f"    Tools: {', '.join(server.tools)}")
        print(f"    Tags: {', '.join(server.tags)}")
        print(f"    Status: {server.status.value}")
    
    # Check health
    print(f"\n🏥 Health Check Results:")
    health_results = await registry.health_check_all()
    
    for server_name, status in health_results.items():
        status_icon = "✅" if status.value == "online" else "❌" if status.value == "offline" else "⚠️"
        print(f"  {status_icon} {server_name}: {status.value}")


async def run_orchestrator_demo():
    """Demonstrate orchestrator capabilities."""
    from simple_orchestrator import SimpleOrchestrator
    
    print("\n🤖 Orchestrator Intelligence Demo")
    print("-" * 40)
    
    orchestrator = SimpleOrchestrator()
    
    test_queries = [
        "What's the weather in London?",
        "Compare weather in New York and Paris",
        "Any alerts in California?",
        "Show forecast for Tokyo"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        result = await orchestrator.process_query(query)
        
        if result["success"]:
            print(f"  🎯 Task: {result['task_type']}")
            print(f"  📍 Locations: {result['locations']}")
            print(f"  ⏱️  Time: {result['execution_time']:.2f}s")
            print(f"  💬 Response: {result['response'][:100]}...")
        else:
            print(f"  ❌ Error: {result['error']}")


async def show_system_status():
    """Show comprehensive system status."""
    try:
        print("\n📊 Production System Status")
        print("-" * 40)
        
        # Show configuration info
        system_info = config_manager.get_system_info()
        for key, value in system_info.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        
        # Try to connect to local server if running
        import httpx
        try:
            server_config = config_manager.get_server_config()
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://{server_config.host}:{server_config.port}/health/quick", timeout=5.0)
                if response.status_code == 200:
                    print("\n✅ Server Status: Running")
                    health_data = response.json()
                    print(f"   Last Check: {health_data.get('timestamp', 'Unknown')}")
                else:
                    print(f"\n⚠️  Server Status: HTTP {response.status_code}")
        except Exception:
            print("\n❌ Server Status: Not running or unreachable")
        
    except Exception as e:
        logger.error(f"Error showing system status: {e}")
        print(f"❌ Error retrieving system status: {e}")





def show_configuration():
    """Show production configuration."""
    print("\n⚙️  Production Configuration")
    print("-" * 40)
    
    # Show system info
    try:
        info = config_manager.get_system_info()
        for key, value in info.items():
            icon = "🔧"
            if "version" in key: icon = "🌟"
            elif "environment" in key: icon = "🌍"
            elif "security" in key: icon = "🔒"
            elif "server" in key: icon = "🖥️"
            
            print(f"{icon} {key.replace('_', ' ').title()}: {value}")
        
        print(f"\n� Security Configuration:")
        security = config_manager.get_security_config()
        print(f"  CORS Enabled: {security.enable_cors}")
        print(f"  API Key Required: {security.api_key_required}")
        print(f"  Rate Limit: {security.rate_limit_per_minute}/min")
        
        print(f"\n🌐 Server Configuration:")
        server = config_manager.get_server_config()
        print(f"  Host: {server.host}")
        print(f"  Port: {server.port}")
        print(f"  Max Connections: {server.max_connections}")
        print(f"  Timeout: {server.timeout}s")
        
    except Exception as e:
        logger.error(f"Error showing configuration: {e}")
        print(f"❌ Error retrieving configuration: {e}")


async def run_full_demo():
    """Run the comprehensive demo."""
    from demo import SystemDemo
    
    demo = SystemDemo()
    await demo.run_full_demo()


async def main():
    """Main application entry point."""
    show_banner()
    
    while True:
        try:
            show_menu()
            choice = input(f"\n💭 Choose an option (1-7): ").strip()
            
            if choice == "1":
                await run_interactive_client()
            elif choice == "2":
                await run_server_discovery()
            elif choice == "3":
                await run_orchestrator_demo()
            elif choice == "4":
                await show_system_status()
            elif choice == "5":
                show_configuration()
            elif choice == "6":
                await run_full_demo()
            elif choice == "7":
                print(f"\n👋 Goodbye! Thanks for using the Production MCP Weather System!")
                logger.info("Interactive session ended by user")
                break
            else:
                print("❌ Invalid choice. Please select 1-7.")
            
            # Pause before showing menu again
            if choice != "8":
                input("\nPress Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye! Thanks for using the Agentic MCP Weather System!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("Please try again or check the system status.")


def start_server(host: str = None, port: int = None):
    """Start the production server."""
    try:
        logger.info("Starting production weather server...")
        
        # Override config if host/port provided
        if host:
            import os
            os.environ['SERVER_HOST'] = host
        if port:
            import os
            os.environ['SERVER_PORT'] = str(port)
        
        from weather import main as start_weather_server
        start_weather_server()
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(f"❌ Server startup failed: {e}")


def validate_configuration() -> bool:
    """Validate the current configuration."""
    try:
        from config import validate_config
        is_valid = validate_config()
        
        if is_valid:
            print("✅ Configuration is valid")
        else:
            print("❌ Configuration validation failed")
            
        return is_valid
        
    except Exception as e:
        logger.error(f"Configuration validation error: {e}")
        print(f"❌ Configuration validation error: {e}")
        return False


def cli_mode():
    """Command-line interface mode for production operations."""
    if len(sys.argv) < 2:
        print("🌟 Production MCP Weather System")
        print("\nUsage:")
        print("  python main.py server [--host HOST] [--port PORT]  # Start production server")
        print("  python main.py start                              # Start production server")
        print("  python main.py status                             # Show system status")
        print("  python main.py config                             # Show configuration")
        print("  python main.py validate                           # Validate configuration")
        print("  python main.py interactive                        # Start interactive mode (dev only)")
        print("  python main.py demo                               # Run demonstration")
        print("  python main.py servers                            # Show server registry")
        return
    
    command = sys.argv[1].lower()
    
    if command == "start" or command == "server":
        # Parse host and port arguments
        host = None
        port = None
        
        args = sys.argv[2:]
        i = 0
        while i < len(args):
            if args[i] == "--host" and i + 1 < len(args):
                host = args[i + 1]
                i += 2
            elif args[i] == "--port" and i + 1 < len(args):
                port = int(args[i + 1])
                i += 2
            else:
                i += 1
        
        start_server(host, port)
    elif command == "status":
        asyncio.run(show_system_status())
    elif command == "config":
        show_configuration()
    elif command == "validate":
        validate_configuration()
    elif command == "interactive":
        asyncio.run(run_interactive_client())
    elif command == "demo":
        asyncio.run(run_full_demo())
    elif command == "servers":
        asyncio.run(run_server_discovery())
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python main.py' for available commands")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli_mode()
    else:
        asyncio.run(main())
