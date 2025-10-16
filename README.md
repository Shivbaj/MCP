# Agentic MCP Weather Intelligence System 🌤️🤖

A comprehensive **Agentic Model Context Protocol (MCP)** system that provides intelligent weather services through orchestrated multi-agent architecture. Built for scalable agentic applications with **full Docker support** and **Streamlit Web UI** for easy deployment and interaction.

## 🌟 Key Features

### 🌐 **Web Interface**
- **Streamlit Chat UI**: ChatGPT-like interface at `http://localhost:8501`
- **Real-time Interactions**: Direct communication with weather agents
- **Visual Dashboard**: System health monitoring and agent status
- **Mobile Responsive**: Works on desktop, tablet, and mobile devices

### 🤖 **Multi-Agent Coordination**
- **Smart Alert Agent**: Proactive weather monitoring and personalized alerts
- **Weather Intelligence Agent**: Multi-source data aggregation and analysis  
- **Travel Agent**: Location-based weather planning and recommendations
- **Agent Coordination Hub**: Centralized orchestration of all weather agents

### 🐳 **Docker-First Architecture**
- **Complete Containerization**: Weather server + Ollama LLM + Streamlit UI + Setup automation
- **Multi-Service Orchestration**: Production-ready microservices architecture
- **Production Ready**: Optimized Dockerfile with security best practices and health checks
- **One-Command Deployment**: Full system startup with `./start-docker.sh`

### 🔧 **Modular Architecture**
- **Server Registry**: Automatic discovery and management of MCP servers
- **Agent Orchestrator**: Intelligent workflow coordination with local LLM  
- **Multi-Agent Support**: Extensible framework for specialized weather agents
- **Health Monitoring**: Real-time status tracking with comprehensive health endpoints
- **API-First Design**: RESTful APIs with interactive documentation at `/docs`

### 🤖 **Advanced Agentic Capabilities**
- **Natural Language Processing**: Understand complex weather queries through LLM integration
- **Intelligent Task Routing**: Automatically delegate queries to specialized agents
- **Multi-Location Coordination**: Compare and analyze weather across multiple cities simultaneously
- **Proactive Alert System**: Smart monitoring with personalized notifications and thresholds
- **Local LLM Integration**: Ollama-powered reasoning and decision making
- **Context-Aware Responses**: Maintain conversation history and learning

### 🌐 **Comprehensive Weather Services**
- **Real-Time Weather**: Current conditions for any city worldwide via multiple APIs
- **Advanced Forecasting**: Detailed predictions using National Weather Service API
- **Smart Alert System**: Weather warnings, emergency notifications, and custom thresholds
- **Multi-Source Intelligence**: Data fusion from weather.gov, wttr.in, and additional sources
- **Travel Planning**: Location-based weather analysis for trip planning and recommendations

## 🏗️ **System Architecture**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Docker Network: weather-mcp-network                  │
│                                                                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────┐ │
│  │ Streamlit UI    │  │ Weather MCP     │  │ Ollama LLM      │  │ Setup   │ │
│  │ :8501           │  │ Server :8000    │  │ Server :11434   │  │ Agent   │ │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ (Init)  │ │
│  │ │   Chat UI   │ │  │ │   MCP API   │ │  │ │   Models:   │ │  │ ┌─────┐ │ │
│  │ │   Dashboard │◄┼──┼─┤   Health    │◄┼──┼─┤   - llama3  │ │  │ │Auto │ │ │
│  │ │   Monitoring│ │  │ │   Agent Hub │ │  │ │   - phi3    │ │  │ │Setup│ │ │
│  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────┘ │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────┘ │
│           │                     │                     │              │      │
└───────────┼─────────────────────┼─────────────────────┼──────────────┼──────┘
            │                     │                     │              │
            │                     │                     │              │
┌───────────▼─────────────────────▼─────────────────────▼──────────────▼──────┐
│                              Host System                                      │
│   🌐 http://localhost:8501   (Streamlit Chat Interface)                      │
│   🔧 http://localhost:8000   (Weather API + Agent Coordination)              │
│   🤖 http://localhost:11434  (Ollama LLM Engine)                             │
│   📚 http://localhost:8000/docs (Interactive API Documentation)              │
└───────────────────────────────────────────────────────────────────────────────┘
```

### **Agent Coordination Flow**
```
User Query ─► Streamlit UI ─► Agent Coordination Hub ─► Specialized Agents
                  │                       │                      │
                  │                       │              ┌─────────────┐
                  │                       └──────────────┤Smart Alert  │
                  │                                      │Agent        │
                  │                              ┌───────┤Weather Intel│
                  │                              │       │Travel Agent │
                  │                              │       └─────────────┘
                  │                              │              │
                  │                              ▼              ▼
                  │                       Ollama LLM ──► API Results
                  │                              │              │
                  └──────────── Response ◄───────┴──────────────┘
```

## ⚡ **TL;DR - Get Started in 3 Commands**

```bash
git clone <your-repo-url> && cd weather
chmod +x *.sh && ./start-docker.sh
# ✅ Chat Interface: http://localhost:8501
# ✅ API Server: http://localhost:8000  
# ✅ System ready with Streamlit UI!
```

**What you get instantly:**
- 🌐 **Streamlit Chat Interface** at `http://localhost:8501` - ChatGPT-like weather assistant
- 🔧 **Weather API** at `http://localhost:8000` - Full MCP server with agent coordination  
- 📚 **API Docs** at `http://localhost:8000/docs` - Interactive OpenAPI documentation
- 🤖 **Ollama LLM** at `http://localhost:11434` - Local AI models for intelligent responses

## 📋 **Requirements**

- **Docker** (20.10 or higher) with Docker Compose
- **8GB+ RAM** (for Ollama LLM models: llama3 + phi3)
- **15GB+ disk space** (for container images + models + logs)
- **Internet connection** (for weather APIs and initial model downloads)
- **Ports available**: 8000 (API), 8501 (Streamlit), 11434 (Ollama)

## 🚀 **Quick Start with Docker**

### Option 1: Complete System with Convenience Scripts (Recommended)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd weather-mcp-agent

# 2. Make scripts executable (Linux/macOS)
chmod +x *.sh

# 3. Validate your environment (optional but recommended)
./validate-docker.sh

# 4. Start the complete system (one command!)
./start-docker.sh

# 5. For verbose output and logs
./start-docker.sh --verbose

# 6. Stop the system when done
./stop-docker.sh
```

### Option 1b: Manual Docker Commands

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd weather-mcp-agent

# 2. Start the complete system (Weather Server + Ollama + Models)
docker-compose up -d

# 3. Monitor the startup process
docker-compose logs -f

# 4. Wait for model downloads (first run only, may take 5-10 minutes)
# You'll see: "Models ready!" when everything is set up

# 5. Test the system
curl http://localhost:8000/health
```

**System will be available at:**
- **🌐 Streamlit Chat UI**: http://localhost:8501 (Primary Interface)
- **🔧 Weather API**: http://localhost:8000 (REST API + Agent Hub)  
- **🤖 Ollama LLM**: http://localhost:11434 (AI Models)
- **📚 API Documentation**: http://localhost:8000/docs (Interactive Docs)

### Option 2: Development Setup with Demo

```bash
# Start system and run demo
docker-compose --profile demo up

# Or run demo separately after system is up
docker-compose up -d
docker-compose run weather-demo
```

### Option 3: Local Development (Non-Docker)

```bash
# 1. Install Ollama locally
brew install ollama  # macOS
# or download from https://ollama.ai/download

# 2. Start Ollama and pull models
ollama serve &
ollama pull llama3
ollama pull phi3

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Environment configuration is ready!
# The .env file is already set up for local development
# For production, copy .env.production.template to .env.production and customize

# 5. Start the weather server
python main.py server
```

## 🐳 **Docker Management Commands**

### Convenience Scripts (Recommended)

```bash
# Development/testing
./start-docker.sh                    # Default setup
./start-docker.sh --dev              # Development mode (live reload)
./start-docker.sh --demo             # Include demo client
./start-docker.sh --verbose          # Show detailed logs

# Production deployment
./start-docker.sh --prod             # Production configuration
./start-docker.sh --prod --build     # Production with fresh build

# Management
./stop-docker.sh                     # Stop (can restart)
./stop-docker.sh --cleanup           # Remove containers
./stop-docker.sh --remove-data       # Remove everything including models
```

### Manual Docker Commands

```bash
# Default setup
docker-compose up -d

# Development mode (with live reload)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Production mode (optimized settings)  
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f weather-server
docker-compose logs -f ollama

# Stop all services
docker-compose down

# Restart services
docker-compose restart

# Rebuild and restart (after code changes)
docker-compose up -d --build

# Pull latest images
docker-compose pull
```

### Environment Configurations

| Environment | Features | Use Case |
|-------------|----------|----------|
| **Default** | Standard settings, API key disabled | Local development & testing |
| **Development** | Live reload, debug logging, relaxed security | Active development |
| **Production** | Optimized performance, security enabled, resource limits | Production deployment |

### Maintenance Commands

```bash
# Check service status
docker-compose ps

# Access container shell
docker-compose exec weather-server bash
docker-compose exec ollama bash

# View system resources
docker-compose top

# Clean up (removes containers, networks, volumes)
docker-compose down -v --remove-orphans

# Remove all unused Docker resources
docker system prune -a
```

### Development Commands

```bash
# Run with demo profile
docker-compose --profile demo up

# Override environment variables
ENVIRONMENT=development docker-compose up -d

# Run single command in container
docker-compose run weather-server python --version
docker-compose run weather-server python demo.py

# Mount local code for development
# (uncomment volume in docker-compose.yml: - .:/app)
```

## 📚 **Usage Examples**

### 🌐 **Primary: Streamlit Chat Interface** (Recommended)

**Open http://localhost:8501 and try these:**

```
💬 "What's the weather like in San Francisco right now?"
💬 "Set up weather alerts for New York with temperature thresholds"  
💬 "Compare weather conditions in London, Paris, and Tokyo"
💬 "Plan my outdoor activities for this weekend in Seattle"
💬 "Any severe weather alerts for California today?"
💬 "What's the best time to travel to Miami this week?"
```

**Features:**
- 🤖 **Natural Language Processing**: Just type like you're chatting with ChatGPT
- 📊 **Visual Dashboard**: Real-time agent status and system health monitoring
- 💾 **Conversation History**: Maintains context across multiple queries
- 📱 **Mobile Responsive**: Works perfectly on phones and tablets

### 🔧 **API Testing (Advanced Users)**

```bash
# System Health Check
curl http://localhost:8000/health

# Agent Coordination Status
curl http://localhost:8000/info

# Direct Weather Query
curl -X POST http://localhost:8000/tools/get_weather \
  -H "Content-Type: application/json" \
  -d '{"city": "San Francisco"}'

# Smart Alert Setup via API
curl -X POST http://localhost:8000/tools/setup_smart_alerts \
  -H "Content-Type: application/json" \
  -d '{
    "locations": ["New York", "Boston"], 
    "alert_types": ["severe_weather", "temperature_extreme"],
    "thresholds": {"temperature_high": 85, "temperature_low": 32}
  }'

# Multi-Location Weather Intelligence
curl -X POST http://localhost:8000/tools/get_weather_intelligence \
  -H "Content-Type: application/json" \
  -d '{"locations": ["London", "Paris", "Rome"], "analysis_type": "comparison"}'
```

### 🐍 **Python Integration**

```python
# Direct Agent Usage
from agent_coordination_hub import AgentCoordinationHub
from smart_alert_agent import AlertAgent

# Initialize coordination system
hub = AgentCoordinationHub()
result = await hub.process_request("Weather in Tokyo with travel recommendations")

# Smart alerts with custom thresholds
alert_agent = AlertAgent()
config = {
    "locations": ["San Francisco", "Seattle"],
    "alert_types": ["severe_weather", "temperature_extreme"], 
    "thresholds": {"temperature_high": 80, "temperature_low": 40}
}
alerts = await alert_agent.setup_smart_alerts(config)
```

## 🛠️ **Docker Troubleshooting**

### Common Issues and Solutions

**Issue: Ollama container fails to start**
```bash
# Check if port 11434 is already in use
lsof -i :11434
# If occupied, stop the local Ollama service
brew services stop ollama

# Check container logs
docker-compose logs ollama
```

**Issue: Model download fails or times out**
```bash
# Manually pull models with more verbose output
docker-compose exec ollama ollama pull llama3
docker-compose exec ollama ollama pull phi3

# Check available disk space (models are 4GB+ each)
docker system df
```

**Issue: Weather server can't connect to Ollama**
```bash
# Check network connectivity
docker-compose exec weather-server curl http://ollama:11434/api/version

# Verify Ollama health
curl http://localhost:11434/api/version

# Check container network
docker network ls
docker network inspect weather-mcp-network
```

**Issue: Out of memory errors**
```bash
# Check Docker memory limits
docker stats

# Increase Docker Desktop memory limit to 8GB+
# Docker Desktop > Settings > Resources > Memory

# Monitor container memory usage
docker-compose exec weather-server free -h
```

**Issue: Port conflicts**
```bash
# Check what's using port 8000
lsof -i :8000

# Use different ports
SERVER_PORT=8080 docker-compose up -d

# Or modify docker-compose.yml ports section
```

### Performance Optimization

```bash
# Pre-pull all images
docker-compose pull

# Build with cache optimization
DOCKER_BUILDKIT=1 docker-compose build

# Limit container resources
# Add to docker-compose.yml under services:
#   weather-server:
#     deploy:
#       resources:
#         limits:
#           memory: 2g
#         reservations:
#           memory: 1g
```

### Logs and Debugging

```bash
# Detailed logging
LOG_LEVEL=DEBUG docker-compose up -d

# Follow all logs with timestamps
docker-compose logs -f -t

# Export logs for analysis
docker-compose logs > system-logs.txt

# Access container filesystems
docker-compose exec weather-server ls -la /app/logs/
```

## ⚙️ **Environment Configuration**

### Environment Files Overview

This project includes a committed `.env` file optimized for local development:

| File | Purpose | Committed to Git |
|------|---------|------------------|
| `.env` | Local development defaults | ✅ Yes |
| `.env.example` | Template with all options | ✅ Yes |
| `.env.production.template` | Production template | ✅ Yes |
| `.env.production` | Your production config | ❌ No (create locally) |
| `.env.local` | Personal overrides | ❌ No (ignored) |

### Local Development

The `.env` file is **ready to use** with safe defaults:

```bash
# Clone and run immediately - no .env setup needed!
git clone <your-repo>
cd weather-mcp-agent
./start-docker.sh
```

**Local Development Features:**
- ✅ `ENVIRONMENT=development`
- ✅ Debug logging enabled
- ✅ CORS allows localhost origins
- ✅ API key requirement disabled
- ✅ High rate limits for testing
- ✅ Raw data and execution logs included

### Customization

Create `.env.local` for personal overrides (ignored by git):

```bash
# .env.local - personal overrides
LOG_LEVEL=DEBUG
OLLAMA_MODEL=phi3
SERVER_PORT=8001
```

### Environment Variables Priority

1. **Environment variables** (highest priority)
2. **`.env.local`** (personal overrides)
3. **`.env`** (committed defaults)

## 🚀 **Production Deployment with Docker**

### Step 1: Production Environment Configuration

```bash
# 1. Clone to production server
git clone <your-repo-url>
cd weather-mcp-agent

# 2. Create production environment file
cp .env.production.template .env.production

# 3. Edit production settings (REQUIRED - update all sensitive values)
nano .env.production
```

**Key Production Settings:**
```bash
ENVIRONMENT=production
API_KEY_REQUIRED=true
API_KEY=your-secure-production-key
ALLOWED_ORIGINS=https://yourdomain.com
RATE_LIMIT_PER_MINUTE=60
LOG_LEVEL=INFO
```

### Step 2: SSL/TLS Configuration (Optional)

```bash
# Add SSL certificates to docker-compose.yml
mkdir -p ./ssl
# Copy your cert.pem and key.pem to ./ssl/

# Update .env.production
SSL_CERT_PATH=/app/ssl/cert.pem
SSL_KEY_PATH=/app/ssl/key.pem
```

### Step 3: Production Deployment

```bash
# Method 1: Using convenience script (recommended)
./start-docker.sh --build

# Method 2: Manual deployment
docker-compose -f docker-compose.yml --env-file .env.production up -d

# Method 3: With custom configuration
docker-compose up -d --build
```

### Step 4: Production Verification

```bash
# Check all services are running
docker-compose ps

# Verify health endpoints
curl https://yourdomain.com:8000/health
curl https://yourdomain.com:8000/info

# Check logs for any issues
docker-compose logs -f --tail=100

# Method 4: Docker with external Ollama
docker build -t weather-mcp .
docker run -p 8000:8000 --env-file .env --add-host=host.docker.internal:host-gateway weather-mcp
```

### Production Endpoints:
- 🏥 `GET /health` - Comprehensive health check with service validation
- ⚡ `GET /health/quick` - Fast health check without external calls
- 📊 `GET /info` - Server capabilities and metadata
- 🌤️ `POST /tools/get_weather` - Current weather (rate limited)
- 📅 `POST /tools/get_forecast` - Weather forecast (validated coordinates)
- 🚨 `POST /tools/get_alerts` - Weather alerts (US states only)

### Management Commands:

```bash
# Production server management
python main.py start         # Start production server
python main.py status        # System health and status
python main.py config        # View current configuration
python main.py validate      # Validate configuration

# Development/testing (disabled in production)
python main.py interactive   # Interactive client mode
python main.py demo          # System demonstration
python main.py servers       # Server registry info
```

## 📁 **Project Structure**

```
weather/
├── 🌐 Web Interface
│   └── streamlit_app.py             # Streamlit Chat UI (Primary Interface)
├── 🤖 Agent Coordination System  
│   ├── agent_coordination_hub.py    # Central agent coordinator
│   ├── smart_alert_agent.py         # Proactive weather monitoring agent
│   ├── weather_intelligence_agent.py # Multi-source data analysis agent
│   └── travel_agent.py              # Location-based travel planning agent
├── � Core MCP Server
│   ├── main.py                      # Production entry point & CLI management
│   ├── weather.py                   # Weather MCP server implementation
│   ├── config.py                    # Configuration management
│   ├── server_registry.py           # Server discovery & health monitoring
│   └── health_server.py             # Health check endpoints
├── 🚀 Orchestration & Workflows
│   ├── simple_orchestrator.py       # Basic agentic workflow orchestrator
│   └── agent_orchestrator.py        # Advanced LangGraph orchestrator
├── 🛠️ Development & Testing
│   ├── mcp_client.py               # Interactive client for testing
│   ├── demo.py                     # System demonstration scripts
│   └── run_server.py               # Alternative server startup
├── � Docker & Deployment
│   ├── Dockerfile                   # Production container image
│   ├── docker-compose.yml           # Multi-service orchestration
│   ├── start-docker.sh              # Comprehensive startup script
│   ├── stop-docker.sh               # Clean shutdown script
│   └── setup-ollama.sh              # Ollama model setup automation
├── 📋 Configuration & Dependencies
│   ├── requirements.txt             # Python dependencies
│   ├── pyproject.toml              # Project metadata (v0.2.0)
│   ├── .env                        # Environment variables (Docker-ready)
│   └── .env.example                # Configuration template
└── 📚 Documentation
    ├── README.md                   # This comprehensive guide
    ├── SETUP.md                    # Quick setup instructions
    ├── DOCKER.md                   # Docker-specific documentation
    ├── DEPLOYMENT.md               # Production deployment guide
    ├── WORKING_SYSTEM_SUMMARY.md   # System status & test cases
    ├── AGENT_COORDINATION_GUIDE.md # Agent development guide
    └── CONTRIBUTING.md             # Contribution guidelines
```

## 💬 **Interactive Usage Examples**

### 🌐 **Streamlit Chat Interface** (http://localhost:8501)

The **primary way** to interact with your weather intelligence system:

**🔮 Smart Weather Queries:**
```
💬 "What's the weather like in London right now?"
🤖 "🌤️ London Weather Update:
    🌡️ Temperature: 15°C (feels like 13°C)  
    🌧️ Conditions: Light drizzle
    💨 Wind: 12 mph from the west
    📊 Humidity: 78%"

💬 "Set up weather alerts for my commute route"  
🤖 "I'll set up smart alerts for your locations. What cities should I monitor?"

💬 "Compare weather in New York, London, and Tokyo"
🤖 "🌍 Multi-City Weather Comparison:
    🗽 New York: 22°C, Sunny, Perfect for outdoor activities
    🇬🇧 London: 15°C, Overcast, Light jacket recommended  
    🗾 Tokyo: 28°C, Humid, Stay hydrated!"
```

**� Advanced Features:**
- **Conversation Memory**: Maintains context across questions
- **Visual Dashboard**: Real-time system health and agent status
- **Mobile Responsive**: Perfect interface for phones and tablets
- **Multi-Agent Coordination**: Automatic routing to specialized weather agents

### 🛠️ **API Command Examples** (Advanced Users)

```bash
# System Status & Health
curl http://localhost:8000/health
curl http://localhost:8000/info

# Agent Coordination
curl -X POST http://localhost:8000/agent/coordinate \
  -H "Content-Type: application/json" \
  -d '{"query": "Weather alerts for California with travel advice"}'
```

## 🛠️ **API Integration Examples**

### **Direct Server API Calls**

```bash
# Get current weather
curl -X POST http://localhost:8000/tools/get_weather \
  -H "Content-Type: application/json" \
  -d '{"city": "London"}'

# Get forecast (requires coordinates)  
curl -X POST http://localhost:8000/tools/get_forecast \
  -H "Content-Type: application/json" \
  -d '{"latitude": 51.5074, "longitude": -0.1278}'

# Get weather alerts (US states only)
curl -X POST http://localhost:8000/tools/get_alerts \
  -H "Content-Type: application/json" \
  -d '{"state": "CA"}'
```

### **Server Discovery & Health**

```bash
# Check server health
curl http://localhost:8000/health

# Get server capabilities
curl http://localhost:8000/info
```

## 🔧 **Extending the System**

### **Adding New MCP Servers**

```python
# Register a new server in server_registry.py
from server_registry import registry, MCPServer

# Define new server
finance_server = MCPServer(
    name="finance-server",
    host="localhost", 
    port=8001,
    description="Financial data and stock information",
    tools=["get_stock_price", "get_market_news", "analyze_portfolio"],
    tags=["finance", "stocks", "market"]
)

# Register it
registry.register_server(finance_server)
```

### **Custom Task Types**

```python
# Extend TaskType enum in simple_orchestrator.py
class TaskType(Enum):
    WEATHER_QUERY = "weather_query"
    FORECAST_ANALYSIS = "forecast_analysis"
    ALERT_MONITORING = "alert_monitoring"
    MULTI_LOCATION = "multi_location"
    FINANCIAL_ANALYSIS = "financial_analysis"  # New!
    GENERAL_INQUIRY = "general_inquiry"
```

## 🎯 **Agentic Design Principles**

### **1. Modularity**
- Each component has a single, clear responsibility
- Easy to extend with new servers and capabilities
- Loose coupling between orchestrator and servers

### **2. Intelligent Routing**
- Task classification determines workflow path
- Location extraction enables multi-location queries
- Error handling with graceful fallbacks

### **3. Scalability**
- Server registry supports dynamic server addition
- Health monitoring for automatic failover
- Async operations for concurrent processing

### **4. Observability**
- Detailed execution logs for debugging
- Performance metrics and timing
- Health status monitoring

## 🔮 **Advanced Features (Optional)**

### **LangGraph Integration**

For more sophisticated agentic workflows, enable the advanced orchestrator:

```python
# Install additional dependencies
uv add langgraph langchain-ollama

# Use agent_orchestrator.py instead of simple_orchestrator.py
from agent_orchestrator import WeatherOrchestrator

# Requires Ollama running locally
ollama serve
```

### **Multi-Agent Coordination**

The system is designed to support multi-agent scenarios:

```python
# Example: Weather + Travel planning agent
travel_query = "What's the weather like in my travel destinations this week?"
# → Orchestrator coordinates:
#   1. Extract travel destinations  
#   2. Get weather for each location
#   3. Get forecasts for travel dates
#   4. Provide travel recommendations
```

## 📊 **Monitoring & Debugging**

### **Health Checks**
```bash
# Check all servers
💬 You: servers

📊 Found 1 registered servers:
   ✅ Online: 1
   ❌ Offline: 0  
   ⚠️  Error: 0
   ❓ Unknown: 0
```

### **Execution Logs**
Every query provides detailed execution tracing:
```
🔍 Execution Log:
   1. Classified task as: weather_query
   2. Extracted locations: ['London']
   3. Gathered weather data for 1 locations
   4. Generated response
```

## 🔒 **Production Security**

### Environment Variables

Required for production deployment:

```bash
# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
ENVIRONMENT=production

# Security
API_KEY_REQUIRED=true
API_KEY=your-secure-api-key-here
RATE_LIMIT_PER_MINUTE=100
ALLOWED_ORIGINS=https://yourdomain.com

# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=/var/log/weather-mcp/server.log
```

### Security Features

- **Input validation** with Pydantic models
- **Rate limiting** per endpoint (configurable)
- **API key authentication** (optional)
- **CORS protection** with configurable origins
- **Request size limits** to prevent DoS
- **Comprehensive logging** for audit trails
- **Error sanitization** to prevent information leakage

## � **Production Monitoring**

### Health Checks

```bash
# Quick health check
curl http://localhost:8000/health/quick

# Comprehensive health check (includes external APIs)
curl http://localhost:8000/health

# Server info and capabilities
curl http://localhost:8000/info
```

### Logging

Production logs are structured and include:
- Request/response logging
- Error tracking with stack traces
- Performance metrics
- Security events (rate limiting, auth failures)

```bash
# View logs (if using file logging)
tail -f /var/log/weather-mcp/server.log

# Check log level
python main.py config | grep -i log
```

### Performance Optimization

- **Async request handling** with httpx
- **Connection pooling** for external APIs
- **Request timeout controls**
- **Exponential backoff** for API retries
- **Response caching** (configurable)
- **Resource limits** and rate limiting

## �🚨 **Troubleshooting**

### Common Production Issues:

1. **Server won't start**: Check port availability and environment variables
   ```bash
   # Check port usage
   lsof -ti:8000
   
   # Validate configuration
   python main.py validate
   
   # Check environment
   python main.py config
   ```

2. **Ollama connection issues**: Ensure Ollama is running and accessible
   ```bash
   # Check if Ollama is running
   ollama list
   
   # If not running, start Ollama
   ollama serve
   
   # Test connection to Ollama
   curl http://localhost:11434/api/version
   
   # Verify model is available
   ollama run llama3 "Hello, test message"
   ```

2. **High memory usage**: Adjust worker count and connection limits
   ```bash
   # Reduce workers in production
   uvicorn weather:app --workers 2 --max-requests 1000
   ```

3. **API timeouts**: External weather services may be slow
   ```bash
   # Check API status
   curl -w "%{time_total}\n" http://localhost:8000/health
   ```

4. **Rate limiting issues**: Adjust limits in environment variables
   ```bash
   # In .env file
   RATE_LIMIT_PER_MINUTE=200
   SERVER_TIMEOUT=45.0
   ```

### Log Analysis

```bash
# Find errors in logs
grep -i error /var/log/weather-mcp/server.log

# Check API performance
grep "response_time" /var/log/weather-mcp/server.log

# Monitor rate limiting
grep "rate.*limit" /var/log/weather-mcp/server.log
```

## 🤝 **Contributing**

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Add tests** for new functionality
5. **Run the test suite**: `uv run main.py test`
6. **Commit your changes**: `git commit -m 'Add amazing feature'`
7. **Push to the branch**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**

### Areas for Contribution:
- **New MCP Servers**: Add weather-adjacent services (traffic, events, etc.)
- **Enhanced NLP**: Improve location extraction and query understanding  
- **Advanced Orchestration**: Implement complex multi-step workflows
- **Data Sources**: Integrate additional weather APIs and services
- **Documentation**: Improve guides and examples
- **Production Features**: Add monitoring, caching, and performance improvements
- **Security Enhancements**: Additional authentication methods and security hardening

## ✅ **Docker Deployment Checklist**

### Pre-deployment
- [ ] Docker Engine 20.10+ installed
- [ ] Docker Compose v2.0+ or docker-compose v1.29+ installed  
- [ ] System has 8GB+ RAM available
- [ ] 10GB+ disk space for Ollama models
- [ ] Internet connectivity for API access and model downloads

### Environment Setup
- [ ] Repository cloned and scripts made executable (`chmod +x *.sh`)
- [ ] Environment validated (`./validate-docker.sh`)
- [ ] Production environment configured (`.env.production`)
- [ ] SSL certificates configured (if using HTTPS)

### Deployment Verification
- [ ] All containers started successfully (`docker-compose ps`)
- [ ] Health checks passing (`curl localhost:8000/health`)
- [ ] Ollama models downloaded (`docker-compose logs ollama-setup`)
- [ ] Weather API endpoints responding (`curl localhost:8000/tools/get_weather`)
- [ ] Logs show no errors (`docker-compose logs`)

### Production Readiness
- [ ] API keys configured and secure
- [ ] Rate limiting configured appropriately
- [ ] CORS settings configured for your domain
- [ ] Monitoring and alerting configured
- [ ] Backup strategy for configuration and data
- [ ] Resource limits set for containers

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎬 **Demo Scenarios** 

**🌐 Open http://localhost:8501 and try these intelligent weather workflows:**

### 🏃‍♂️ **Personal Planning**
```
💬 "Plan my outdoor workout routine for San Francisco this week"
💬 "Should I bring an umbrella to my meeting in Seattle tomorrow?"
💬 "What's the best day for a picnic in Central Park this weekend?"  
💬 "When should I schedule my outdoor photography session in London?"
```

### ✈️ **Travel Intelligence** 
```
💬 "I'm flying from New York to Los Angeles tomorrow - any weather concerns?"
💬 "Compare weather conditions for my business trip: Boston, Chicago, Denver"
💬 "Best time to visit Tokyo this month based on weather patterns?"
💬 "Should I pack winter clothes for my trip to Montreal next week?"
```

### 🚨 **Smart Monitoring**
```  
💬 "Set up weather alerts for my daily commute from Brooklyn to Manhattan"
💬 "Monitor severe weather for my company's offices in California and Texas"
💬 "Alert me if temperature drops below freezing in Chicago this week"
💬 "Watch for storm systems affecting my weekend camping trip in Yosemite"
```

### 🏢 **Business Applications**
```
💬 "Weather impact analysis for our retail stores in Florida, Georgia, and South Carolina"  
💬 "Construction weather forecast for our project sites in Denver and Phoenix"
💬 "Event planning weather assessment for outdoor venues this month"
```

**Each query demonstrates:**
- 🤖 **Multi-Agent Coordination**: Automatic routing to specialized agents
- 🧠 **Context Awareness**: Understanding complex, multi-part requests
- 📊 **Intelligent Analysis**: Data fusion from multiple weather sources  
- 💡 **Proactive Recommendations**: Actionable insights beyond raw data

## 📚 **Dependencies**

See `requirements.txt` for the complete list of dependencies. Key packages:

- **FastAPI**: REST API framework
- **LangChain**: LLM integration (optional for advanced features)
- **LangGraph**: Advanced agentic orchestration
- **MCP**: Model Context Protocol implementation
- **Requests/HTTPX**: HTTP client libraries
- **Pydantic**: Data validation

## 🙏 **Acknowledgments**

- Built on the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) framework
- Weather data from [NWS API](https://www.weather.gov/documentation/services-web-api) and [wttr.in](https://wttr.in/)
- Inspired by the agentic AI community

## 📊 **Current System Status** (Updated: October 16, 2025)

### **✅ Live Services**
- **🌐 Streamlit Chat Interface**: http://localhost:8501 ✅ **HEALTHY**
- **🔧 Weather API + Agent Hub**: http://localhost:8000 ✅ **HEALTHY**  
- **🤖 Ollama LLM Engine**: http://localhost:11434 ✅ **HEALTHY**
- **📚 Interactive API Documentation**: http://localhost:8000/docs ✅ **AVAILABLE**

### **🤖 Active Agents**
- **Smart Alert Agent**: ✅ Proactive weather monitoring with custom thresholds
- **Weather Intelligence Agent**: ✅ Multi-source data analysis and forecasting
- **Travel Agent**: ✅ Location-based planning and recommendations  
- **Agent Coordination Hub**: ✅ Central orchestration and routing system

### **💡 Try It Now**
1. **Open**: http://localhost:8501 (Streamlit Chat)
2. **Ask**: *"Set up weather alerts for San Francisco with temperature thresholds"*
3. **Watch**: Multi-agent coordination in action!

### **📈 System Health**
```json
{
  "status": "healthy",
  "services": {
    "nws_api": "available",
    "wttr_in": "available", 
    "ollama": "healthy"
  },
  "performance": {
    "response_time_ms": 2135.61,
    "memory_usage": "available"
  },
  "environment": "production"
}
```

---

**Built with ❤️ for the agentic AI community** | **Extensible • Modular • Production-Ready**
**Version 0.2.0** | **Multi-Agent Coordination** | **Docker-Native** | **Streamlit Interface**