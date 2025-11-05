"""AI helper utilities for Gemini API integration."""
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai
from utils.logger import setup_logger
import yaml

logger = setup_logger(__name__)

# Load environment variables
load_dotenv()

def load_config() -> dict:
    """Load configuration from config.yaml."""
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

def initialize_gemini() -> bool:
    """
    Initialize Gemini API with API key from environment.
    
    Returns:
        True if successful, False otherwise
    """
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key or api_key == 'your_gemini_api_key_here':
        logger.error("Gemini API key not configured")
        return False
    
    try:
        genai.configure(api_key=api_key)
        logger.info("Gemini API initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Gemini API: {e}")
        return False

def get_gemini_model(model_name: Optional[str] = None) -> Any:
    """
    Get configured Gemini model instance.
    
    Args:
        model_name: Optional model name override
        
    Returns:
        Gemini model instance
    """
    if not initialize_gemini():
        raise ValueError("Gemini API not configured")
    
    # Load model config
    config = load_config()
    model_config = config.get('ai_agent', {}).get('model', {})
    
    if model_name is None:
        model_name = model_config.get('name', 'gemini-1.5-flash')
    
    # Create generation config
    generation_config = {
        'temperature': model_config.get('temperature', 0.7),
        'top_p': model_config.get('top_p', 0.9),
        'max_output_tokens': model_config.get('max_tokens', 2048),
    }
    
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config
    )
    
    return model

def generate_text(prompt: str, model_name: Optional[str] = None) -> Optional[str]:
    """
    Generate text using Gemini API.
    
    Args:
        prompt: Input prompt
        model_name: Optional model name override
        
    Returns:
        Generated text or None if failed
    """
    try:
        model = get_gemini_model(model_name)
        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text
        else:
            logger.warning("Empty response from Gemini API")
            return None
            
    except Exception as e:
        logger.error(f"Error generating text with Gemini: {e}")
        return None

def generate_structured_response(prompt: str, system_context: Optional[str] = None) -> Optional[str]:
    """
    Generate structured response with optional system context.
    
    Args:
        prompt: User prompt
        system_context: Optional system context to prepend
        
    Returns:
        Generated response or None
    """
    full_prompt = prompt
    if system_context:
        full_prompt = f"{system_context}\n\n{prompt}"
    
    return generate_text(full_prompt)

def extract_json_from_response(response_text: str) -> Optional[Dict]:
    """
    Extract JSON from AI response that might contain markdown code blocks.
    
    Args:
        response_text: AI-generated text potentially containing JSON
        
    Returns:
        Parsed JSON dictionary or None
    """
    import json
    import re
    
    if not response_text:
        return None
    
    # Try to extract JSON from markdown code blocks
    json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    matches = re.findall(json_pattern, response_text, re.DOTALL)
    
    if matches:
        try:
            return json.loads(matches[0])
        except json.JSONDecodeError:
            pass
    
    # Try to parse the entire response as JSON
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Try to find JSON-like structure
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            try:
                return json.loads(response_text[json_start:json_end])
            except json.JSONDecodeError:
                pass
    
    logger.warning("Could not extract JSON from response")
    return None

if __name__ == "__main__":
    # Test AI helpers
    print("Testing Gemini AI helpers...")
    
    if initialize_gemini():
        print("✓ Gemini API initialized")
        
        # Test simple generation
        response = generate_text("Say hello in a professional way.")
        if response:
            print(f"✓ Generated response: {response[:100]}...")
        else:
            print("✗ Failed to generate response")
    else:
        print("✗ Gemini API not configured")

