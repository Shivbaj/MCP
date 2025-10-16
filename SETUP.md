# ⚡ Quick Setup Guide - Weather Intelligence System

## 🐳 **Docker Setup (Recommended - Production Ready)**

### Prerequisites
- Docker 20.10+ with Docker Compose
- 8GB+ RAM (for AI models)
- 15GB+ disk space  
- Internet connection

### One-Command Setup
```bash
git clone <your-repo-url> weather
cd weather
chmod +x *.sh
./start-docker.sh
```

**✅ System Ready!**
- 🌐 **Chat Interface**: http://localhost:8501 (Primary)
- 🔧 **API Server**: http://localhost:8000  
- 🤖 **AI Models**: http://localhost:11434
- 📚 **API Docs**: http://localhost:8000/docs

---

## 🐍 **Local Python Setup (Development)**

### Prerequisites  
- Python 3.13+
- Git
- Ollama (for AI features)

### Step 1: Install Ollama
```bash
# macOS
brew install ollama

# Linux/WSL
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve &

# Install required models (4GB+ each)
ollama pull llama3
ollama pull phi3

# Verify installation
ollama list
```

### Step 2: Python Environment

#### Using uv (Recommended)
```bash
git clone <your-repo-url> weather
cd weather
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync  # Installs all dependencies automatically
```

#### Using pip
```bash
git clone <your-repo-url> weather
cd weather
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Step 3: Start Services

#### Option A: Full System (Streamlit + API + Agents)
```bash
# Terminal 1: Ensure Ollama is running
ollama serve

# Terminal 2: Start API server
python main.py server

# Terminal 3: Start Streamlit interface  
streamlit run streamlit_app.py --server.port 8501
```

#### Option B: API Only
```bash
ollama serve &
python main.py start
```

### Step 4: Verify Installation
```bash
# Check system health
python main.py validate

# Test API endpoints
curl http://localhost:8000/health

# Open Streamlit interface (if running)
# http://localhost:8501
```

## 🔧 **Configuration**

### Environment Variables
- **Development**: `.env` file is pre-configured
- **Production**: Copy `.env.example` to `.env.production` and customize

### Key Settings
```bash
# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
ENVIRONMENT=development

# AI Integration  
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3

# Security (Production)
API_KEY_REQUIRED=false
RATE_LIMIT_PER_MINUTE=300
```

## 🧪 **First Test**

### Using Streamlit (Easiest)
1. Open http://localhost:8501
2. Type: `"What's the weather in San Francisco?"`
3. Watch the multi-agent system respond!

### Using API
```bash
curl -X POST http://localhost:8000/tools/get_weather \
  -H "Content-Type: application/json" \
  -d '{"city": "London"}'
```

### Using Python
```python
from agent_coordination_hub import AgentCoordinationHub

hub = AgentCoordinationHub()
result = await hub.process_request("Weather in Tokyo with travel tips")
print(result)
```

## ❓ **Troubleshooting**

### Ollama Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Restart Ollama service  
pkill ollama && ollama serve &

# Re-download models if needed
ollama pull llama3
```

### Port Conflicts
```bash
# Check what's using ports
lsof -i :8000  # API server
lsof -i :8501  # Streamlit  
lsof -i :11434 # Ollama

# Use different ports if needed
SERVER_PORT=8080 streamlit run streamlit_app.py --server.port 8502
```

### Memory Issues
- Ensure 8GB+ RAM available
- Close other applications
- Use `ollama pull phi3` (smaller model) instead of llama3

---

## 🚀 **Next Steps**

1. **Explore the Interface**: Try the Streamlit chat at http://localhost:8501
2. **Test Agent Coordination**: Ask complex queries that require multiple agents
3. **Set Up Alerts**: Configure proactive weather monitoring  
4. **Review Documentation**: Check AGENT_COORDINATION_GUIDE.md for advanced features
5. **Production Deployment**: See DEPLOYMENT.md for production setup

That's it! 🚀