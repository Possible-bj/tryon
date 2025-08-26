"""
Configuration utilities for Styled AI processing service
"""

import os
from functools import lru_cache
from config.settings import Settings

@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching
    
    Returns:
        Settings: Application configuration object
    """
    return Settings()

def get_env_var(key: str, default: str = None) -> str:
    """
    Get environment variable with fallback
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        str: Environment variable value or default
    """
    return os.getenv(key, default)

def is_development() -> bool:
    """Check if running in development mode"""
    return get_env_var("ENVIRONMENT", "development").lower() == "development"

def is_production() -> bool:
    """Check if running in production mode"""
    return get_env_var("ENVIRONMENT", "development").lower() == "production"

def get_model_path(model_name: str) -> str:
    """
    Get path to AI model files
    
    Args:
        model_name: Name of the model
        
    Returns:
        str: Path to model directory
    """
    settings = get_settings()
    base_path = settings.MODEL_CACHE_DIR
    return str(base_path / model_name)

# File system paths removed - using in-memory storage instead
