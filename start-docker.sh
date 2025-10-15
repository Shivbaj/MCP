#!/bin/bash

# Weather MCP Docker Startup Script
# Starts the complete Weather MCP system using Docker Compose (supports both legacy and new versions)

set -e

echo "🌤️ Weather MCP System - Docker Startup"
echo "======================================="

# --- Check if Docker is installed ---
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# --- Check if Docker Compose is available (either old or new CLI) ---
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose is not installed. Please install it:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

# --- Check if Docker daemon is running ---
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running. Please start Docker."
    exit 1
fi

# --- Parse CLI arguments ---
DEMO_MODE=false
BUILD_FRESH=false
VERBOSE=false
ENVIRONMENT="default"

while [[ $# -gt 0 ]]; do
    case $1 in
        --demo) DEMO_MODE=true ;;
        --build) BUILD_FRESH=true ;;
        --verbose|-v) VERBOSE=true ;;
        --prod|--production) ENVIRONMENT="production" ;;
        --dev|--development) ENVIRONMENT="development" ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --demo        Start with demo client"
            echo "  --build       Force rebuild of containers"
            echo "  --verbose     Show verbose output"
            echo "  --prod        Use production configuration"
            echo "  --dev         Use development configuration"
            echo "  --help        Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
    shift
done

echo "📋 Configuration:"
echo "   Environment: $ENVIRONMENT"
echo "   Demo mode: $DEMO_MODE"
echo "   Fresh build: $BUILD_FRESH"
echo "   Verbose: $VERBOSE"
echo ""

# --- Stop any running containers ---
echo "🛑 Stopping any existing containers..."
$COMPOSE_CMD down --remove-orphans

# --- Pull latest images ---
if [ "$BUILD_FRESH" = false ]; then
    echo "⬇️ Pulling latest images..."
    $COMPOSE_CMD pull
fi

# --- Build containers if requested ---
if [ "$BUILD_FRESH" = true ]; then
    echo "🔨 Building containers..."
    if [ "$VERBOSE" = true ]; then
        $COMPOSE_CMD build
    else
        $COMPOSE_CMD build --quiet
    fi
fi

# --- Determine compose files ---
COMPOSE_FILES="-f docker-compose.yml"
if [ "$ENVIRONMENT" = "production" ]; then
    COMPOSE_FILES="$COMPOSE_FILES -f docker-compose.prod.yml"
    echo "   Using production configuration..."
elif [ "$ENVIRONMENT" = "development" ]; then
    COMPOSE_FILES="$COMPOSE_FILES -f docker-compose.dev.yml"
    echo "   Using development configuration..."
fi

# --- Determine profiles ---
if [ "$DEMO_MODE" = true ]; then
    echo "   Including demo client..."
    COMPOSE_ARGS="--profile demo"
else
    COMPOSE_ARGS=""
fi

# --- Start the system ---
echo "🚀 Starting Weather MCP System..."
$COMPOSE_CMD $COMPOSE_FILES $COMPOSE_ARGS up -d

echo ""
echo "✅ System started successfully!"
echo ""
echo "🌐 Services available at:"
echo "   • Weather API: http://localhost:8000"
echo "   • API Docs:    http://localhost:8000/docs"  
echo "   • Ollama API:  http://localhost:11434"
echo ""

# --- Quick health checks ---
sleep 3
echo "🔍 Quick health check:"

if curl -s http://localhost:8000/health/quick > /dev/null 2>&1; then
    echo "   ✅ Weather service: Ready"
else
    echo "   ⏳ Weather service: Starting... (may take a moment)"
fi

if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "   ✅ Ollama service: Ready"
else
    echo "   ⏳ Ollama service: Starting... (may take a moment)"
fi

echo ""
echo "📚 Useful commands:"
echo "   View logs:        $COMPOSE_CMD logs -f"
echo "   Stop system:      $COMPOSE_CMD down"
echo "   Restart:          $COMPOSE_CMD restart"
echo "   System status:    $COMPOSE_CMD ps"
echo ""
echo "🎯 Test the API:"
echo "   curl http://localhost:8000/health"
echo "   curl -X POST http://localhost:8000/tools/get_weather -H 'Content-Type: application/json' -d '{\"city\": \"San Francisco\"}'"
