"""
LLM Configuration and Management

This module handles the configuration and initialization of different Language Learning Models
for the AI Multi-Agent Content Creation Pipeline.
"""

import os
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMConfig:
    """Configuration class for Language Learning Models"""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.default_model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.max_tokens = int(os.getenv('MAX_TOKENS', '4000'))
        self.temperature = float(os.getenv('TEMPERATURE', '0.7'))
        
    def validate_api_keys(self) -> Dict[str, bool]:
        """Validate available API keys"""
        return {
            'openai': bool(self.openai_api_key and self.openai_api_key != 'your_openai_api_key_here'),
            'anthropic': bool(self.anthropic_api_key and self.anthropic_api_key != 'your_anthropic_api_key_here'),
            'google': bool(self.google_api_key and self.google_api_key != 'your_google_api_key_here')
        }

def get_llm(
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    **kwargs
) -> ChatOpenAI:
    """
    Get a configured LLM instance
    
    Args:
        model_name: Name of the model to use
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        **kwargs: Additional model parameters
        
    Returns:
        Configured LLM instance
    """
    config = LLMConfig()
    
    # Validate that we have the required API key
    valid_keys = config.validate_api_keys()
    if not valid_keys['openai']:
        raise ValueError(
            "OpenAI API key not found or invalid. Please set OPENAI_API_KEY in your environment variables."
        )
    
    # Use provided parameters or fall back to config defaults
    model = model_name or config.default_model
    temp = temperature if temperature is not None else config.temperature
    tokens = max_tokens or config.max_tokens
    
    return ChatOpenAI(
        model_name=model,
        temperature=temp,
        max_tokens=tokens,
        openai_api_key=config.openai_api_key,
        **kwargs
    )

def configure_llm(agent_role: str) -> ChatOpenAI:
    """
    Configure LLM for specific agent roles with optimized parameters
    
    Args:
        agent_role: The role of the agent (coordinator, researcher, writer, editor, seo)
        
    Returns:
        Configured LLM instance optimized for the agent role
    """
    role_configs = {
        'coordinator': {
            'temperature': 0.3,  # Lower temperature for more structured coordination
            'max_tokens': 2000
        },
        'researcher': {
            'temperature': 0.5,  # Balanced for factual research
            'max_tokens': 3000
        },
        'writer': {
            'temperature': 0.8,  # Higher temperature for creative writing
            'max_tokens': 4000
        },
        'editor': {
            'temperature': 0.4,  # Lower temperature for precise editing
            'max_tokens': 3000
        },
        'seo': {
            'temperature': 0.3,  # Lower temperature for technical SEO tasks
            'max_tokens': 2000
        }
    }
    
    config = role_configs.get(agent_role, {})
    return get_llm(**config)

def get_available_models() -> Dict[str, Dict[str, Any]]:
    """
    Get information about available models
    
    Returns:
        Dictionary with model information
    """
    return {
        'gpt-3.5-turbo': {
            'name': 'GPT-3.5 Turbo',
            'provider': 'OpenAI',
            'cost': 'Low',
            'context_length': 16385,
            'description': 'Fast and cost-effective for most tasks'
        },
        'gpt-4': {
            'name': 'GPT-4',
            'provider': 'OpenAI', 
            'cost': 'High',
            'context_length': 8192,
            'description': 'Highest quality reasoning and complex tasks'
        },
        'gpt-4-turbo': {
            'name': 'GPT-4 Turbo',
            'provider': 'OpenAI',
            'cost': 'Medium-High',
            'context_length': 128000,
            'description': 'Large context window with improved performance'
        }
    }

def test_llm_connection() -> Dict[str, Any]:
    """
    Test LLM connection and return status
    
    Returns:
        Dictionary with connection status and model info
    """
    try:
        llm = get_llm()
        # Test with a simple prompt
        response = llm.invoke("Hello! Please respond with 'Connection successful'")
        
        return {
            'status': 'success',
            'model': llm.model_name,
            'response': response.content,
            'message': 'LLM connection successful'
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'message': 'Failed to connect to LLM'
        } 