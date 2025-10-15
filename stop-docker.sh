#!/bin/bash

# Weather MCP Docker Stop Script
# This script cleanly stops the Weather MCP system

set -e

echo "🛑 Weather MCP System - Docker Stop"
echo "==================================="

# Parse command line arguments
CLEANUP=false
REMOVE_VOLUMES=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --cleanup)
            CLEANUP=true
            shift
            ;;
        --remove-data)
            REMOVE_VOLUMES=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --cleanup       Remove containers and networks"
            echo "  --remove-data   Also remove data volumes (Ollama models)"
            echo "  --help          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                Stop containers (keep for restart)"
            echo "  $0 --cleanup      Stop and remove containers"  
            echo "  $0 --remove-data  Stop and remove everything including models"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "📋 Configuration:"
echo "   Cleanup containers: $CLEANUP"
echo "   Remove data volumes: $REMOVE_VOLUMES"
echo ""

# Show current status
echo "📊 Current container status:"
./././docker-compose-wrapper.sh-wrapper.sh-wrapper.sh ps

echo ""
echo "🛑 Stopping containers..."

if [ "$REMOVE_VOLUMES" = true ]; then
    echo "⚠️  WARNING: This will remove all data including Ollama models!"
    echo "   Models will need to be re-downloaded on next start."
    echo ""
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ./././docker-compose-wrapper.sh-wrapper.sh-wrapper.sh down -v --remove-orphans
        echo "✅ Stopped and removed all containers, networks, and volumes"
    else
        echo "❌ Operation cancelled"
        exit 0
    fi
elif [ "$CLEANUP" = true ]; then
    ./././docker-compose-wrapper.sh-wrapper.sh-wrapper.sh down --remove-orphans
    echo "✅ Stopped and removed containers and networks"
    echo "💾 Data volumes preserved (Ollama models kept)"
else
    ./././docker-compose-wrapper.sh-wrapper.sh-wrapper.sh stop
    echo "✅ Containers stopped (can be restarted with './././docker-compose-wrapper.sh-wrapper.sh-wrapper.sh start')"
fi

echo ""
echo "🔍 Final status:"
./././docker-compose-wrapper.sh-wrapper.sh-wrapper.sh ps

if [ "$REMOVE_VOLUMES" = false ] && [ "$CLEANUP" = false ]; then
    echo ""
    echo "💡 To restart quickly: ./././docker-compose-wrapper.sh-wrapper.sh-wrapper.sh start"
    echo "💡 To restart fresh:   ./././docker-compose-wrapper.sh-wrapper.sh-wrapper.sh up -d"
fi

if [ "$CLEANUP" = true ] && [ "$REMOVE_VOLUMES" = false ]; then
    echo ""
    echo "💾 Ollama models are preserved in volume: $(docker volume ls -q | grep ollama || echo 'none')"
    echo "💡 Next startup will be faster (models already downloaded)"
fi