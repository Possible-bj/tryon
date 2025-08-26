# config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Styled AI - Data Science Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # AI/ML Models (Essential)
    TENSORFLOW_MODEL_PATH: Optional[str] = None
    TORCH_MODEL_PATH: Optional[str] = None
    MODEL_CACHE_DIR: Path = Path("models")
    
    # Image Processing (Essential)
    AVATAR_WIDTH: int = 512
    AVATAR_HEIGHT: int = 768
    AVATAR_QUALITY: int = 95
    GARMENT_RESOLUTION: int = 1024
    
    # AI Processing (Essential)
    GPU_ENABLED: bool = True
    INFERENCE_TIMEOUT: int = 300  # 5 minutes
    
    # Memory Management (Essential)
    MAX_CACHE_SIZE: int = 100
    CACHE_CLEANUP_THRESHOLD: int = 80
    
    # Logging (Essential)
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True