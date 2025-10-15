# Production Dockerfile for Weather MCP Server
FROM python:3.13-slim

# Set environment variables for production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=production
ENV OLLAMA_HOST=http://ollama:11434

# Create non-root user for security
RUN groupadd -r weather && useradd -r -g weather weather

# Set working directory
WORKDIR /app

# Install system dependencies including curl for health checks
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and pyproject.toml first for better caching
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Change ownership to non-root user
RUN chown -R weather:weather /app

# Switch to non-root user
USER weather

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/quick || exit 1

# Run the application using main.py for proper initialization
CMD ["python", "main.py", "server", "--host", "0.0.0.0", "--port", "8000"]