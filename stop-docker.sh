#!/bin/bash

# Weather MCP Docker Stop Script
# This script cleanly stops the Weather MCP system

set -e

echo "🛑 Weather MCP System - Docker Stop"
echo "==================================="

# Use standard compose file
COMPOSE_FILE="docker-compose.yml"

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
            echo "  --help, -h      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Stop containers only"
            echo "  $0 --cleanup          # Stop and remove containers/networks"
            echo "  $0 --remove-data      # Stop and remove everything including data"
            exit 0
            ;;
        *)
            echo "❌ Unknown option: $1"
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
docker-compose -f $COMPOSE_FILE ps 2>/dev/null || echo "No containers found"

echo ""
echo "🛑 Stopping containers..."

if [ "$REMOVE_VOLUMES" = true ]; then
    echo "⚠️  WARNING: This will remove all data including Ollama models!"
    echo "   Models will need to be re-downloaded on next start."
    echo ""
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose -f $COMPOSE_FILE down -v --remove-orphans
        echo "✅ Stopped and removed all containers, networks, and volumes"
    else
        echo "❌ Operation cancelled"
        exit 0
    fi
elif [ "$CLEANUP" = true ]; then
    docker-compose -f $COMPOSE_FILE down --remove-orphans
    echo "✅ Stopped and removed containers and networks"
else
    docker-compose -f $COMPOSE_FILE stop
    echo "✅ Containers stopped"
fi

echo ""
echo "📊 Final status:"
docker-compose -f $COMPOSE_FILE ps 2>/dev/null || echo "All containers stopped"

echo ""
echo "✅ Stop operation completed!"
echo ""
echo "💡 Quick commands:"
echo "   Restart: './start-docker.sh'"
echo "   Clean restart: './start-docker.sh --build'"
echo "   View logs: 'docker-compose -f $COMPOSE_FILE logs -f'"
