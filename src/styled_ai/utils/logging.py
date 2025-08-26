"""
Logging utilities for Styled AI processing service
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from .config import get_settings

def setup_logging():
    """
    Setup logging configuration for the application
    
    Configures console and file logging with appropriate levels
    and formatting.
    """
    settings = get_settings()
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for general logs
    file_handler = RotatingFileHandler(
        log_dir / "styled_ai.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # File handler for errors
    error_handler = RotatingFileHandler(
        log_dir / "styled_ai_errors.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # Log startup message
    logging.info("Logging configured successfully")
    logging.info(f"Log level: {settings.LOG_LEVEL}")
    logging.info(f"Log directory: {log_dir.absolute()}")

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)

def log_processing_start(request_id: str, operation: str):
    """Log the start of a processing operation"""
    logger = get_logger(__name__)
    logger.info(f"Starting {operation} for request: {request_id}")

def log_processing_complete(request_id: str, operation: str, duration: float):
    """Log the completion of a processing operation"""
    logger = get_logger(__name__)
    logger.info(f"Completed {operation} for request: {request_id} in {duration:.2f}s")

def log_processing_error(request_id: str, operation: str, error: Exception):
    """Log a processing error"""
    logger = get_logger(__name__)
    logger.error(f"Error in {operation} for request: {request_id}: {str(error)}", exc_info=True)

def log_model_operation(model_name: str, operation: str, status: str):
    """Log AI model operations"""
    logger = get_logger(__name__)
    logger.info(f"Model {model_name}: {operation} - {status}")

def log_performance_metrics(operation: str, duration: float, success: bool):
    """Log performance metrics"""
    logger = get_logger(__name__)
    level = logging.INFO if success else logging.WARNING
    logger.log(level, f"Performance: {operation} took {duration:.2f}s (success: {success})")
