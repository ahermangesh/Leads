"""Logging utilities for the Lead Scraper project."""
import os
import logging
from datetime import datetime
from pathlib import Path

def setup_logger(name, level=logging.INFO):
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name (typically __name__)
        level: Logging level
    
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("data")
    log_dir.mkdir(exist_ok=True)
    
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Return existing logger if handlers are already set up
    if logger.handlers:
        return logger
    
    # Log file path with timestamp
    log_file = log_dir / "scraper.log"

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # File handler with UTF-8 encoding to handle special characters
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler with utf-8 encoding if possible
    try:
        # Check if console supports UTF-8
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)
    except Exception:
        pass  # Silently skip console handler if it fails
    
    return logger