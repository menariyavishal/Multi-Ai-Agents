"""
LLM Factory – returns LangChain-compatible chat models.
Supports Groq, Hugging Face, and Mock LLMs for testing.
Implements caching, timeouts, and basic retry logic.
"""
import os
from pydantic import SecretStr
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.language_models import BaseLanguageModel
from app.config import Config
from app.core.constants import MODEL_CONFIGS
from app.core.logger import get_logger

logger = get_logger(__name__)

class LLMFactory:
    """Factory to create and cache LLM instances per agent role."""
    
    _instances = {}  # Cache: agent_role -> LLM instance
    
    @classmethod
    def get_llm(cls, agent_role: str) -> BaseLanguageModel:
        """Return a LangChain language model for the given agent role.
        
        Set USE_MOCK_LLM=true environment variable to use mock LLMs for testing.
        """
        if agent_role in cls._instances:
            return cls._instances[agent_role]
        
        # Check if mock mode is enabled
        use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
        
        if use_mock:
            from app.core.mock_llm import MockLLM
            llm = MockLLM(agent_role=agent_role)
            logger.info(f"Created Mock LLM for {agent_role} (mock mode enabled)")
            cls._instances[agent_role] = llm
            return llm
        
        config = MODEL_CONFIGS.get(agent_role)
        if not config:
            raise ValueError(f"No model configuration for agent role: {agent_role}")
        
        provider = config["provider"]
        model_name = config["name"]
        temperature = config["temperature"]
        
        if provider == "huggingface":
            if not Config.HF_API_TOKEN:
                raise ValueError("HF_API_TOKEN is not set. Please add it to .env")
            # Use HuggingFaceEndpoint (langchain-huggingface package - no deprecation warnings)
            llm = HuggingFaceEndpoint(
                repo_id=model_name,
                huggingfacehub_api_token=Config.HF_API_TOKEN,
                temperature=temperature,
                max_new_tokens=512
            ) # pyright: ignore[reportCallIssue]
            logger.info(f"Created Hugging Face LLM for {agent_role} using {model_name}")
            
        elif provider == "groq":
            if not Config.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY is not set. Please add it to .env")
            llm = ChatGroq(
                model=model_name,
                api_key=SecretStr(Config.GROQ_API_KEY),
                temperature=temperature,
                timeout=Config.LLM_TIMEOUT,
                max_retries=Config.LLM_MAX_RETRIES
            )
            logger.info(f"Created Groq LLM for {agent_role} using {model_name}")
            
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Cache the instance
        cls._instances[agent_role] = llm
        return llm
    
    @classmethod
    def clear_cache(cls):
        """Clear cached LLM instances (useful for testing)."""
        cls._instances.clear()
        logger.info("LLM factory cache cleared")
