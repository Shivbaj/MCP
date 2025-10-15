# Quick Setup Guide

## Prerequisites
- Python 3.13+
- Git
- Internet connection
- Ollama (for LLM features)

## Step 1: Install Ollama
```bash
# Install Ollama
brew install ollama

# Start Ollama (keep running)
ollama serve &

# Install Llama3 model
ollama pull llama3

# Verify
ollama list
```

## Step 2: Python Setup

### Using uv (Recommended)
```bash
git clone <your-repo-url> && cd weather-mcp-agent && curl -LsSf https://astral.sh/uv/install.sh | sh && uv sync
```

### Using pip
```bash
git clone <your-repo-url> && cd weather-mcp-agent && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

## Step 3: Quick Start
```bash
# Terminal 1: Start Ollama (if not running)
ollama serve

# Terminal 2: Start weather server
python main.py start

# Terminal 3: Test the system
python main.py status
```

## First Test
```bash
python main.py validate
```

That's it! 🚀