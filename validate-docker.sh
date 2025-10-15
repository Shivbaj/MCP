#!/bin/bash

# Docker Environment Validation Script
# Checks if Docker and Docker Compose are properly installed

set -e

echo "🔍 Docker Environment Validation"
echo "================================"

# Check Docker
echo -n "Docker: "
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d ' ' -f3 | cut -d ',' -f1)
    echo "✅ Found Docker $DOCKER_VERSION"
    
    # Check if Docker daemon is running
    if docker info &> /dev/null; then
        echo "   ✅ Docker daemon is running"
    else
        echo "   ❌ Docker daemon is not running. Please start Docker."
        exit 1
    fi
else
    echo "❌ Docker not found. Please install Docker:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker Compose
echo -n "Docker Compose: "
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version | cut -d ' ' -f3 | cut -d ',' -f1)
    echo "✅ Found docker-compose $COMPOSE_VERSION"
    COMPOSE_CMD="docker-compose"
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version --short)
    echo "✅ Found docker compose $COMPOSE_VERSION (v2)"
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose not found. Please install Docker Compose:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

# Create a compose command wrapper
cat > docker-compose-wrapper.sh << EOF
#!/bin/bash
# Auto-generated wrapper for Docker Compose
exec $COMPOSE_CMD "\$@"
EOF
chmod +x docker-compose-wrapper.sh

# Validate docker-compose.yml
echo -n "Compose Config: "
if ./docker-compose-wrapper.sh -f docker-compose.yml config --quiet; then
    echo "✅ docker-compose.yml is valid"
else
    echo "❌ docker-compose.yml has errors"
    exit 1
fi

# Check memory
echo -n "System Memory: "
if command -v free &> /dev/null; then
    TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$TOTAL_MEM" -ge 8 ]; then
        echo "✅ ${TOTAL_MEM}GB (sufficient for Ollama)"
    else
        echo "⚠️  ${TOTAL_MEM}GB (recommended: 8GB+ for Ollama models)"
    fi
elif command -v vm_stat &> /dev/null; then
    # macOS
    PAGES=$(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//')
    TOTAL_GB=$((PAGES * 4096 / 1024 / 1024 / 1024))
    if [ "$TOTAL_GB" -ge 8 ]; then
        echo "✅ ${TOTAL_GB}GB+ (sufficient for Ollama)"
    else
        echo "⚠️  Available memory may be limited for Ollama models"
    fi
else
    echo "⚠️  Cannot determine memory (ensure 8GB+ available)"
fi

# Check disk space
echo -n "Disk Space: "
AVAILABLE_GB=$(df . | awk 'NR==2{print int($4/1024/1024)}')
if [ "$AVAILABLE_GB" -ge 10 ]; then
    echo "✅ ${AVAILABLE_GB}GB available"
else
    echo "⚠️  ${AVAILABLE_GB}GB available (may need more for Ollama models)"
fi

echo ""
echo "🎉 Environment validation complete!"
echo ""
echo "Next steps:"
echo "  ./start-docker.sh          # Start the system"
echo "  ./start-docker.sh --help   # See all options"

# Update scripts to use the wrapper
echo ""
echo "📝 Updating scripts for your Docker Compose version..."
sed -i.bak "s/docker-compose/\.\/docker-compose-wrapper.sh/g" start-docker.sh stop-docker.sh
echo "✅ Scripts updated to use: $COMPOSE_CMD"