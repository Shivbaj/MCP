#!/bin/bash

# Ollama Setup Script for Weather MCP System
# This script sets up Ollama and downloads the required Llama3 model

set -e

echo "🦙 Setting up Ollama for Weather MCP System..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo " Ollama is not installed. Please install it first:"
    echo "   macOS/Linux: brew install ollama"
    echo "   Or visit: https://ollama.ai/download"
    exit 1
fi

echo "Ollama found"

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/version &> /dev/null; then
    echo "  Ollama is not running. Starting Ollama..."
    
    # Start Ollama in the background
    ollama serve &
    OLLAMA_PID=$!
    
    # Wait for Ollama to start
    echo "⏳ Waiting for Ollama to start..."
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/version &> /dev/null; then
            echo " Ollama is now running (PID: $OLLAMA_PID)"
            break
        fi
        if [ $i -eq 30 ]; then
            echo " Ollama failed to start within 30 seconds"
            exit 1
        fi
        sleep 1
    done
else
    echo " Ollama is already running"
fi

# Check if Llama3 model is already installed
if ollama list | grep -q "llama3"; then
    echo " Llama3 model is already installed"
else
    echo " Downloading Llama3 model (this may take several minutes)..."
    ollama pull llama3
    echo "Llama3 model downloaded successfully"
fi

# Test the model
echo "🧪 Testing Llama3 model..."
if echo "Hello, this is a test message. Respond with 'OK' if you can read this." | ollama run llama3 --timeout 10s | grep -q -i "ok"; then
    echo "Llama3 model is working correctly"
else
    echo " Llama3 model test completed (check output above)"
fi

# Show installed models
echo ""
echo " Installed Ollama models:"
ollama list

echo ""
echo "Ollama setup complete!"
echo ""
echo "Next steps:"
echo "1. Keep Ollama running: ollama serve"
echo "2. Set up your environment: cp .env.example .env"
echo "3. Start the weather server: python main.py start"
echo ""
echo "For Docker deployment:"
echo "  docker-compose up -d"