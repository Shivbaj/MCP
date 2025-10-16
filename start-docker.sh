#!/bin/bash

# Universal Docker startup script for Weather MCP System
# This script handles both development and production environments

set -e

# Default values
ENVIRONMENT="production"
COMPOSE_FILE="docker-compose.yml"
SERVICES=""
BUILD=false
LOGS=false
DOWN=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}Weather MCP System Docker Manager${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dev                 Start in development mode"
    echo "  --prod                Start in production mode (default)"
    echo "  --build               Force rebuild of containers"
    echo "  --logs                Show logs after starting"
    echo "  --down                Stop and remove containers"
    echo "  --demo                Include demo services"
    echo "  --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --dev             # Start in development mode"
    echo "  $0 --prod --build    # Start in production with rebuild"
    echo "  $0 --down            # Stop all services"
    echo "  $0 --logs            # Start and show logs"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            ENVIRONMENT="development"
            shift
            ;;
        --prod)
            ENVIRONMENT="production"
            shift
            ;;
        --build)
            BUILD=true
            shift
            ;;
        --logs)
            LOGS=true
            shift
            ;;
        --down)
            DOWN=true
            shift
            ;;
        --demo)
            SERVICES="--profile demo"
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

print_header

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    print_error "docker-compose is not installed. Please install docker-compose and try again."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        print_status "Created .env from .env.example"
    else
        cat > .env << EOF
# Environment Configuration
ENVIRONMENT=${ENVIRONMENT}
LOG_LEVEL=INFO
DEBUG=false
RATE_LIMIT_PER_MINUTE=100
API_KEY_REQUIRED=false
ENABLE_CORS=true

# Ollama Configuration
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama3

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
EOF
        print_status "Created default .env file"
    fi
fi

# Update .env with current environment
sed -i.bak "s/ENVIRONMENT=.*/ENVIRONMENT=${ENVIRONMENT}/" .env && rm .env.bak
print_status "Set ENVIRONMENT=${ENVIRONMENT} in .env"

# Set environment-specific variables
export ENVIRONMENT=${ENVIRONMENT}
if [ "$ENVIRONMENT" = "development" ]; then
    export LOG_LEVEL="DEBUG"
    export DEBUG="true"
    export RATE_LIMIT_PER_MINUTE="1000"
else
    export LOG_LEVEL="INFO"
    export DEBUG="false"
    export RATE_LIMIT_PER_MINUTE="100"
fi

# Handle down command
if [ "$DOWN" = true ]; then
    print_status "Stopping and removing containers..."
    docker-compose -f ${COMPOSE_FILE} down --volumes --remove-orphans
    print_status "All containers stopped and removed."
    exit 0
fi

# Build options
BUILD_FLAGS=""
if [ "$BUILD" = true ]; then
    BUILD_FLAGS="--build"
    print_status "Force rebuilding containers..."
fi

print_status "Starting Weather MCP System in ${ENVIRONMENT} mode..."

# Start services
docker-compose -f ${COMPOSE_FILE} up -d ${BUILD_FLAGS} ${SERVICES}

# Wait for services to be healthy
print_status "Waiting for services to be ready..."
sleep 10

# Check service health
print_status "Checking service health..."

# Check Ollama
if curl -s http://localhost:11434/api/version > /dev/null; then
    print_status "✅ Ollama is running (http://localhost:11434)"
else
    print_warning "⚠️ Ollama may still be starting up..."
fi

# Check Weather Server
if curl -s http://localhost:8000/health/quick > /dev/null; then
    print_status "✅ Weather Server is running (http://localhost:8000)"
else
    print_warning "⚠️ Weather Server may still be starting up..."
fi

# Check Streamlit UI
if curl -s http://localhost:8501 > /dev/null; then
    print_status "✅ Streamlit UI is running (http://localhost:8501)"
else
    print_warning "⚠️ Streamlit UI may still be starting up..."
fi

print_status "System startup complete!"
echo ""
echo -e "${BLUE}Available Services:${NC}"
echo "  🌐 Weather API: http://localhost:8000"
echo "  📊 Streamlit UI: http://localhost:8501"
echo "  🤖 Ollama LLM: http://localhost:11434"
echo ""
echo -e "${BLUE}Quick Test Commands:${NC}"
echo "  curl http://localhost:8000/health"
echo "  curl -X POST http://localhost:8000/query -H 'Content-Type: application/json' -d '{\"query\":\"Weather in Tokyo\"}'"
echo ""

if [ "$LOGS" = true ]; then
    print_status "Showing logs (press Ctrl+C to exit)..."
    docker-compose -f ${COMPOSE_FILE} logs -f
fi

print_status "Use '$0 --down' to stop all services"