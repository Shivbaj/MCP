"""
MCP Server Registry and Discovery System

This module provides functionality to discover, register, and manage MCP servers
for agentic applications.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import httpx
import asyncio
import json
import os
from enum import Enum


class ServerStatus(Enum):
    """Server status enumeration."""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class MCPServer:
    """Represents an MCP server with its capabilities."""
    name: str
    host: str
    port: int
    description: str
    tools: List[str] = field(default_factory=list)
    status: ServerStatus = ServerStatus.UNKNOWN
    last_check: Optional[datetime] = None
    capabilities: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    @property
    def base_url(self) -> str:
        """Get the base URL for the server."""
        return f"http://{self.host}:{self.port}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "description": self.description,
            "tools": self.tools,
            "status": self.status.value,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "capabilities": self.capabilities,
            "tags": self.tags,
            "base_url": self.base_url
        }


class MCPServerRegistry:
    """Registry for managing MCP servers."""
    
    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self._initialize_default_servers()
    
    def _initialize_default_servers(self):
        """Initialize with default known servers."""
        # Get weather server URL from environment variable
        weather_server_url = os.environ.get("WEATHER_SERVER_URL", "http://localhost:8000")
        
        # Parse the URL to extract host and port
        if weather_server_url.startswith("http://"):
            url_without_protocol = weather_server_url[7:]  # Remove "http://"
        elif weather_server_url.startswith("https://"):
            url_without_protocol = weather_server_url[8:]  # Remove "https://"
        else:
            url_without_protocol = weather_server_url
        
        if ":" in url_without_protocol:
            host, port_str = url_without_protocol.split(":", 1)
            port = int(port_str)
        else:
            host = url_without_protocol
            port = 8000  # Default port
        
        weather_server = MCPServer(
            name="weather-server",
            host=host, 
            port=port,
            description="Weather information service using NWS API and wttr.in",
            tools=["get_weather", "get_forecast", "get_alerts"],
            tags=["weather", "forecast", "alerts", "location"]
        )
        self.servers[weather_server.name] = weather_server
    
    def register_server(self, server: MCPServer) -> bool:
        """Register a new MCP server."""
        try:
            self.servers[server.name] = server
            return True
        except Exception:
            return False
    
    def get_server(self, name: str) -> Optional[MCPServer]:
        """Get a server by name."""
        return self.servers.get(name)
    
    def list_servers(self, status_filter: Optional[ServerStatus] = None) -> List[MCPServer]:
        """List all servers, optionally filtered by status."""
        servers = list(self.servers.values())
        if status_filter:
            servers = [s for s in servers if s.status == status_filter]
        return servers
    
    def get_servers_by_tag(self, tag: str) -> List[MCPServer]:
        """Get servers that have a specific tag."""
        return [server for server in self.servers.values() if tag in server.tags]
    
    async def health_check(self, server_name: str) -> ServerStatus:
        """Check if a specific server is healthy."""
        server = self.get_server(server_name)
        if not server:
            return ServerStatus.UNKNOWN
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Try to ping the server (assuming it has a health endpoint)
                response = await client.get(f"{server.base_url}/health")
                if response.status_code == 200:
                    server.status = ServerStatus.ONLINE
                else:
                    server.status = ServerStatus.ERROR
        except httpx.ConnectError:
            server.status = ServerStatus.OFFLINE
        except Exception:
            server.status = ServerStatus.ERROR
        
        server.last_check = datetime.now()
        return server.status
    
    async def health_check_all(self) -> Dict[str, ServerStatus]:
        """Check health of all registered servers."""
        tasks = []
        for server_name in self.servers.keys():
            task = self.health_check(server_name)
            tasks.append((server_name, task))
        
        results = {}
        for server_name, task in tasks:
            status = await task
            results[server_name] = status
        
        return results
    
    async def discover_server_capabilities(self, server_name: str) -> Dict[str, Any]:
        """Discover the capabilities of a server."""
        server = self.get_server(server_name)
        if not server:
            return {}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try to get server info/capabilities
                response = await client.get(f"{server.base_url}/info")
                if response.status_code == 200:
                    capabilities = response.json()
                    server.capabilities = capabilities
                    return capabilities
        except Exception:
            pass
        
        return {}
    
    def get_servers_summary(self) -> Dict[str, Any]:
        """Get a summary of all servers and their status."""
        total = len(self.servers)
        online = len([s for s in self.servers.values() if s.status == ServerStatus.ONLINE])
        offline = len([s for s in self.servers.values() if s.status == ServerStatus.OFFLINE])
        error = len([s for s in self.servers.values() if s.status == ServerStatus.ERROR])
        unknown = len([s for s in self.servers.values() if s.status == ServerStatus.UNKNOWN])
        
        return {
            "total_servers": total,
            "online": online,
            "offline": offline,
            "error": error,
            "unknown": unknown,
            "servers": [server.to_dict() for server in self.servers.values()]
        }
    
    def export_registry(self) -> str:
        """Export the registry to JSON format."""
        return json.dumps(self.get_servers_summary(), indent=2)
    
    def import_registry(self, json_data: str) -> bool:
        """Import servers from JSON data."""
        try:
            data = json.loads(json_data)
            for server_data in data.get("servers", []):
                server = MCPServer(
                    name=server_data["name"],
                    host=server_data["host"],
                    port=server_data["port"],
                    description=server_data["description"],
                    tools=server_data.get("tools", []),
                    tags=server_data.get("tags", [])
                )
                self.register_server(server)
            return True
        except Exception:
            return False


# Global registry instance
registry = MCPServerRegistry()


async def main():
    """Example usage of the server registry."""
    print("MCP Server Registry Demo")
    print("=" * 40)
    
    # List all servers
    servers = registry.list_servers()
    print(f"Registered servers: {len(servers)}")
    
    for server in servers:
        print(f"  - {server.name}: {server.base_url}")
    
    print("\nChecking server health...")
    health_results = await registry.health_check_all()
    
    for server_name, status in health_results.items():
        print(f"  {server_name}: {status.value}")
    
    print("\nServer Summary:")
    summary = registry.get_servers_summary()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(main())