# 🤝 Contributing to Weather Intelligence System

Thank you for your interest in contributing to our multi-agent weather intelligence system! 🎉

## **🌟 Current System Overview**

This project includes:
- **🌐 Streamlit Chat Interface** - ChatGPT-like weather assistant  
- **🤖 Multi-Agent Coordination** - Specialized weather, travel, and alert agents
- **🔧 MCP Server** - Production-ready API with health monitoring
- **🐳 Docker Infrastructure** - Complete containerized deployment
- **📊 Real-time Monitoring** - System health and performance tracking

## **🚀 Development Setup**

### Quick Start (Docker)
```bash  
# Fork and clone the repository
git clone https://github.com/YOUR-USERNAME/weather.git
cd weather

# Start development environment
./start-docker.sh --dev

# System ready for development:
# 🌐 Streamlit: http://localhost:8501 (with live reload)
# 🔧 API: http://localhost:8000 (with debug mode)
# 🤖 Ollama: http://localhost:11434
```

### Local Python Development
```bash
# Clone and setup
git clone https://github.com/YOUR-USERNAME/weather.git
cd weather

# Setup with uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync

# Alternative: pip setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Install and start Ollama
brew install ollama  # macOS
ollama serve &
ollama pull llama3

# Create feature branch
git checkout -b feature/your-amazing-feature
```

## Making Changes

1. **Write your code** following Python best practices
2. **Add tests** for new functionality in `test_suite.py`
3. **Update documentation** if needed
4. **Test your changes**:
   ```bash
   uv run main.py test
   ```

## Code Style

- Use Python type hints
- Follow PEP 8 style guide
- Add docstrings for new functions/classes
- Use meaningful variable names

## Submitting Changes

1. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add: your descriptive commit message"
   ```
2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
3. **Open a Pull Request** on GitHub

## Areas to Contribute

- 🔧 New MCP servers and tools
- 🤖 Enhanced AI orchestration
- 📊 Better monitoring and logging
- 🧪 More comprehensive tests
- 📚 Documentation improvements
- 🐛 Bug fixes

## Questions?

Open an issue on GitHub for discussion before starting major changes.

Happy coding! 🚀