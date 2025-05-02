"""Decorators for the lead scraper project."""
import functools
import time
from typing import Any, Callable, TypeVar
import yaml
from .logger import setup_logger

logger = setup_logger(__name__)
T = TypeVar("T")

def load_retry_config() -> dict:
    """Load retry configuration from config.yaml."""
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    return config["retry"]

def retry_with_backoff(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator that retries the function with exponential backoff on failure.
    
    Args:
        func: The function to wrap with retry logic
        
    Returns:
        The wrapped function with retry capability
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        config = load_retry_config()
        max_attempts = config["max_attempts"]
        initial_delay = config["initial_delay"]
        backoff_factor = config["backoff_factor"]
        
        attempt = 0
        while attempt < max_attempts:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                attempt += 1
                if attempt == max_attempts:
                    logger.error(
                        f"Failed after {max_attempts} attempts. Error: {str(e)}"
                    )
                    raise
                
                delay = initial_delay * (backoff_factor ** (attempt - 1))
                logger.warning(
                    f"Attempt {attempt} failed. Retrying in {delay:.1f}s. Error: {str(e)}"
                )
                time.sleep(delay)
        
        raise RuntimeError("Should not reach here")
    
    return wrapper