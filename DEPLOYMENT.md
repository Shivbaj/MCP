# Production Deployment Guide

## Quick Production Setup

### 1. Ollama Setup

```bash
# Install Ollama
brew install ollama  # macOS
# Or download from https://ollama.ai/download

# Start Ollama service
ollama serve &

# Pull required model
ollama pull llama3

# Verify installation
ollama list
```

### 2. Environment Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd weather-mcp-agent

# Create production environment file
cp .env.example .env

# Edit environment variables for your deployment
nano .env
```

### 2. Docker Deployment (Recommended)

#### Option A: Docker Compose with Ollama (Recommended)

```bash
# Start both Ollama and Weather Server
docker-compose up -d

# Initialize Ollama with Llama3 model
docker-compose exec ollama ollama pull llama3

# Check services status
docker-compose ps

# View logs
docker-compose logs -f weather-server
```

#### Option B: Docker with External Ollama

```bash
# Ensure Ollama is running on host
ollama serve &

# Build production image
docker build -t weather-mcp:latest .

# Run with environment file (connecting to host Ollama)
docker run -d \
  --name weather-mcp \
  --env-file .env \
  -p 8000:8000 \
  --add-host=host.docker.internal:host-gateway \
  --restart unless-stopped \
  weather-mcp:latest

# Check container status
docker logs weather-mcp
```

### 3. Direct Python Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Validate configuration
python main.py validate

# Start production server
python main.py start
```

### 4. Production with Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
```

## Production Checklist

### Before Deployment

- [ ] Install and configure Ollama with Llama3 model
- [ ] Verify Ollama is running: `ollama serve`
- [ ] Test Ollama connectivity: `ollama list`
- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Configure secure `API_KEY` if authentication required
- [ ] Set appropriate `ALLOWED_ORIGINS` for CORS
- [ ] Configure log file path and rotation
- [ ] Set resource limits (`MAX_CONNECTIONS`, `RATE_LIMIT_PER_MINUTE`)
- [ ] Test configuration: `python main.py validate`

### Security Hardening

- [ ] Enable API key authentication (`API_KEY_REQUIRED=true`)
- [ ] Restrict CORS origins to your domain only
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules (allow only necessary ports)
- [ ] Set up log monitoring and alerts
- [ ] Regular security updates

### Monitoring Setup

```bash
# Health check endpoint for monitoring
curl http://localhost:8000/health/quick

# Comprehensive health check
curl http://localhost:8000/health

# Server metrics
curl http://localhost:8000/info
```

### Performance Tuning

```bash
# Multiple workers for high traffic
uvicorn weather:app --host 0.0.0.0 --port 8000 --workers 4

# With Gunicorn (alternative)
gunicorn weather:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENVIRONMENT` | No | `production` | Deployment environment |
| `SERVER_HOST` | No | `0.0.0.0` | Server bind address |
| `SERVER_PORT` | No | `8000` | Server port |
| `API_KEY_REQUIRED` | No | `false` | Enable API authentication |
| `API_KEY` | If auth enabled | - | API key for authentication |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `RATE_LIMIT_PER_MINUTE` | No | `100` | API rate limit |
| `OLLAMA_HOST` | No | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | No | `llama3` | Ollama model to use |
| `OLLAMA_TIMEOUT` | No | `30.0` | Ollama request timeout |
| `ENABLE_ADVANCED_ORCHESTRATION` | No | `true` | Enable LLM features |

See `.env.example` for complete list.

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   lsof -i :8000
   # Kill the process or use a different port
   ```

2. **Permission Denied (Docker)**
   ```bash
   # Run as non-root user
   docker run --user $(id -u):$(id -g) ...
   ```

3. **External API Timeouts**
   ```bash
   # Increase timeout in .env
   SERVER_TIMEOUT=45.0
   ```

4. **Ollama Not Responding**
   ```bash
   # Check if Ollama is running
   ps aux | grep ollama
   
   # Restart Ollama
   ollama serve
   
   # Test Ollama API
   curl http://localhost:11434/api/version
   
   # Check available models
   ollama list
   ```

### Log Analysis

```bash
# Real-time log monitoring
tail -f /var/log/weather-mcp/server.log

# Error analysis
grep -i "error\|exception" /var/log/weather-mcp/server.log

# Performance monitoring
grep "response_time" /var/log/weather-mcp/server.log
```

### Health Monitoring

Set up monitoring alerts for:
- `/health/quick` endpoint availability
- Response time > 5 seconds
- Error rate > 1%
- Memory/CPU usage > 80%

## Scaling Considerations

- **Horizontal scaling**: Deploy multiple instances behind load balancer
- **Database**: Add Redis for caching weather data
- **CDN**: Cache static responses for common locations
- **Rate limiting**: Implement distributed rate limiting for multiple instances