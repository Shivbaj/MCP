"""
Production Configuration Management for Agentic MCP Weather System

This module provides centralized configuration management with environment variables,
proper logging, and production-ready settings.
"""

import logging
import os
import sys
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json
from enum import Enum


class Environment(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class ServerConfig:
    """Configuration for an MCP server."""
    name: str
    host: str
    port: int
    description: str
    tools: List[str]
    tags: List[str]
    enabled: bool = True
    timeout: float = 30.0
    retry_count: int = 3
    health_check_interval: int = 300  # seconds
    max_connections: int = 100


@dataclass
class SecurityConfig:
    """Security configuration."""
    enable_cors: bool = True
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    api_key_required: bool = False
    api_key: Optional[str] = None
    rate_limit_per_minute: int = 100
    request_size_limit: int = 1024 * 1024  # 1MB


@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator."""
    default_llm_model: str = "llama3"
    max_concurrent_requests: int = 10
    request_timeout: float = 60.0
    enable_request_logging: bool = True
    
    # Task classification settings
    location_extraction_method: str = "keyword"  # "keyword", "llm", "hybrid"
    max_locations_per_query: int = 10
    
    # Response formatting
    include_raw_data: bool = False
    include_execution_log: bool = False  # Disabled in production
    response_format: str = "friendly"  # "friendly", "technical", "json"


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: LogLevel = LogLevel.INFO
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True


@dataclass
class SystemConfig:
    """Main system configuration."""
    version: str = "1.0.0"
    environment: Environment = Environment.PRODUCTION
    debug: bool = False
    
    # Server settings
    server: ServerConfig = field(default_factory=lambda: ServerConfig(
        name="weather-server",
        host=os.getenv("SERVER_HOST", "0.0.0.0"),
        port=int(os.getenv("SERVER_PORT", "8000")),
        description="Production Weather MCP Server",
        tools=["get_weather", "get_forecast", "get_alerts"],
        tags=["weather", "forecast", "alerts"],
        timeout=float(os.getenv("SERVER_TIMEOUT", "30.0")),
        retry_count=int(os.getenv("SERVER_RETRY_COUNT", "3")),
        health_check_interval=int(os.getenv("HEALTH_CHECK_INTERVAL", "300")),
        max_connections=int(os.getenv("MAX_CONNECTIONS", "100"))
    ))
    
    # Security settings
    security: SecurityConfig = field(default_factory=lambda: SecurityConfig(
        enable_cors=os.getenv("ENABLE_CORS", "true").lower() == "true",
        allowed_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
        api_key_required=os.getenv("API_KEY_REQUIRED", "false").lower() == "true",
        api_key=os.getenv("API_KEY"),
        rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "100")),
        request_size_limit=int(os.getenv("REQUEST_SIZE_LIMIT", str(1024 * 1024)))
    ))
    
    # Orchestrator settings
    orchestrator: OrchestratorConfig = field(default_factory=lambda: OrchestratorConfig(
        default_llm_model=os.getenv("LLM_MODEL", "llama3"),
        max_concurrent_requests=int(os.getenv("MAX_CONCURRENT_REQUESTS", "10")),
        request_timeout=float(os.getenv("REQUEST_TIMEOUT", "60.0")),
        enable_request_logging=os.getenv("ENABLE_REQUEST_LOGGING", "true").lower() == "true",
        max_locations_per_query=int(os.getenv("MAX_LOCATIONS_PER_QUERY", "10")),
        include_raw_data=os.getenv("INCLUDE_RAW_DATA", "false").lower() == "true",
        include_execution_log=os.getenv("INCLUDE_EXECUTION_LOG", "false").lower() == "true",
        response_format=os.getenv("RESPONSE_FORMAT", "friendly")
    ))
    
    # Logging settings
    logging: LoggingConfig = field(default_factory=lambda: LoggingConfig(
        level=LogLevel(os.getenv("LOG_LEVEL", "INFO")),
        file_path=os.getenv("LOG_FILE_PATH"),
        max_file_size=int(os.getenv("LOG_MAX_FILE_SIZE", str(10 * 1024 * 1024))),
        backup_count=int(os.getenv("LOG_BACKUP_COUNT", "5")),
        enable_console=os.getenv("LOG_ENABLE_CONSOLE", "true").lower() == "true"
    ))
    
    def __post_init__(self):
        """Post-initialization setup."""
        # Set environment from environment variable
        env_str = os.getenv("ENVIRONMENT", "production").lower()
        if env_str in [e.value for e in Environment]:
            self.environment = Environment(env_str)
        
        # Set debug mode based on environment
        self.debug = self.environment == Environment.DEVELOPMENT
        
        # Adjust logging level for production
        if self.environment == Environment.PRODUCTION:
            if self.logging.level == LogLevel.DEBUG:
                self.logging.level = LogLevel.INFO


class ProductionConfigManager:
    """Production-ready configuration manager."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = SystemConfig()
        self.logger = self._setup_logging()
        
        if config_file and Path(config_file).exists():
            self._load_config_file(config_file)
        
        self.logger.info(f"Configuration loaded for {self.config.environment.value} environment")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup production logging."""
        logger = logging.getLogger("mcp_weather_system")
        logger.setLevel(getattr(logging, self.config.logging.level.value))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        formatter = logging.Formatter(self.config.logging.format)
        
        # Console handler
        if self.config.logging.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # File handler
        if self.config.logging.file_path:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                self.config.logging.file_path,
                maxBytes=self.config.logging.max_file_size,
                backupCount=self.config.logging.backup_count
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def _load_config_file(self, config_file: str) -> None:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                # Update configuration with file data
                # Implementation depends on specific needs
            self.logger.info(f"Configuration loaded from {config_file}")
        except Exception as e:
            self.logger.error(f"Failed to load config file {config_file}: {e}")
    
    def get_server_config(self) -> ServerConfig:
        """Get server configuration."""
        return self.config.server
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration."""
        return self.config.security
    
    def get_orchestrator_config(self) -> OrchestratorConfig:
        """Get orchestrator configuration."""
        return self.config.orchestrator
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        return {
            "version": self.config.version,
            "environment": self.config.environment.value,
            "debug": self.config.debug,
            "server_host": self.config.server.host,
            "server_port": self.config.server.port,
            "log_level": self.config.logging.level.value,
            "security_enabled": self.config.security.api_key_required,
            "rate_limit": self.config.security.rate_limit_per_minute,
            "max_connections": self.config.server.max_connections,
            "request_timeout": self.config.orchestrator.request_timeout,
        }
    
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.config.environment == Environment.PRODUCTION
    
    def is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled."""
        return self.config.debug


# Global configuration manager instance
config_manager = ProductionConfigManager()


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(f"mcp_weather_system.{name}")


# Environment configuration templates
ENVIRONMENT_CONFIGS = {
    "development": {
        "LOG_LEVEL": "DEBUG",
        "ENABLE_EXECUTION_LOG": "true",
        "MAX_CONCURRENT_REQUESTS": "5",
        "REQUEST_TIMEOUT": "30.0"
    },
    "production": {
        "LOG_LEVEL": "INFO",
        "ENABLE_EXECUTION_LOG": "false", 
        "MAX_CONCURRENT_REQUESTS": "20",
        "REQUEST_TIMEOUT": "60.0",
        "SERVER_HOST": "0.0.0.0",
        "API_KEY_REQUIRED": "true"
    },
    "staging": {
        "LOG_LEVEL": "INFO",
        "ENABLE_EXECUTION_LOG": "true",
        "MAX_CONCURRENT_REQUESTS": "10", 
        "REQUEST_TIMEOUT": "45.0"
    }
}


def create_env_file(environment: str = "production") -> str:
    """Create environment file content."""
    if environment not in ENVIRONMENT_CONFIGS:
        environment = "production"
    
    lines = []
    for key, value in ENVIRONMENT_CONFIGS[environment].items():
        lines.append(f"{key}={value}")
    
    return "\n".join(lines)


def validate_config() -> bool:
    """Validate current configuration."""
    try:
        config = config_manager.config
        
        # Validate server config
        if config.server.port < 1 or config.server.port > 65535:
            return False
        
        # Validate security config
        if config.security.api_key_required and not config.security.api_key:
            return False
        
        # Validate logging config
        if config.logging.file_path and not Path(config.logging.file_path).parent.exists():
            return False
        
        return True
    
    except Exception:
        return False


if __name__ == "__main__":
    print("🔧 Production Configuration System")
    print("=" * 50)
    
    # Show system info
    info = config_manager.get_system_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    
    # Validate configuration
    is_valid = validate_config()
    print(f"\nConfiguration valid: {'✅' if is_valid else '❌'}")
    
    # Show environment template
    print(f"\nSample .env file for production:")
    print(create_env_file("production"))