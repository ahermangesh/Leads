"""Web utilities for browser automation."""
import random
from typing import Dict, Optional
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from .logger import setup_logger
from .decorators import retry_with_backoff

logger = setup_logger(__name__)

def load_config() -> dict:
    """Load web configuration from config.yaml."""
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    return config

def setup_chrome_options(headless: bool = True) -> Options:
    """
    Set up Chrome options for Selenium.
    
    Args:
        headless: Whether to run Chrome in headless mode
        
    Returns:
        Chrome options object
    """
    options = Options()
    
    if headless:
        options.add_argument("--headless")
    
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # Disable automation flags and infobar
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Disable save password prompt
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.notifications": 2
    }
    options.add_experimental_option("prefs", prefs)
    
    return options

def setup_chrome_driver(headless: bool = True) -> webdriver.Chrome:
    """
    Set up Chrome driver with configured options.
    
    Args:
        headless: Whether to run Chrome in headless mode
        
    Returns:
        Configured Chrome webdriver instance
    """
    logger.info(f"Setting up Chrome driver (headless={headless})")
    
    options = setup_chrome_options(headless)
    service = Service(ChromeDriverManager().install())
    
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(60)  # Set page load timeout to 60 seconds
        return driver
    except Exception as e:
        logger.error(f"Failed to setup Chrome driver: {str(e)}")
        raise

def get_random_user_agent() -> str:
    """
    Get a random user agent string.
    
    Returns:
        Random user agent string
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.41",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
    ]
    
    return random.choice(user_agents)

@retry_with_backoff
def create_browser_session(headless: bool = True) -> webdriver.Chrome:
    """
    Create a new browser session with retry capability.
    
    Args:
        headless: Whether to run Chrome in headless mode
        
    Returns:
        Configured Chrome WebDriver instance
    """
    logger.info("Creating new browser session...")
    return setup_chrome_driver(headless)