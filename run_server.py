#!/usr/bin/env python3
"""
Simple script to run the weather MCP server
"""

if __name__ == "__main__":
    from weather import main
    print("Starting weather MCP server on http://localhost:8000")
    print("Available endpoints:")
    print("  POST /tools/get_weather - Get current weather for a city")
    print("  POST /tools/get_forecast - Get forecast for lat/lon coordinates") 
    print("  POST /tools/get_alerts - Get weather alerts for a US state")
    print("\nPress Ctrl+C to stop the server")
    main()