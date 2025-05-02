"""Logger utility for the lead scraper project."""
import logging
import os
from typing import Optional
import yaml

def setup_logger(name: str = "lead_scraper") -> logging.Logger:
    """
    Set up a logger with configured settings from config.yaml.
    
    Args:
        name: The name of the logger instance
        
    Returns:
        A configured logger instance
    """
    # Load config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    logger = logging.getLogger(name)
    logger.setLevel(config["logging"]["level"])

    # Create logs directory if it doesn't exist
    log_file = config["logging"]["file"]
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # File handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger