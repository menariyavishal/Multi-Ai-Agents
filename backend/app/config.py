"""
Configuration management for different environments.
Loads environment variables and provides config classes.
"""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get the absolute path to the project root (backend/ directory)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:
    """Base configuration - common settings for all environments."""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
    
    # LLM API Keys
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    
    # Database paths (absolute to avoid working directory issues)
    SQLITE_PATH = os.environ.get('SQLITE_PATH', os.path.join(BASE_DIR, 'data', 'nueuro.db'))
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
    
    # Rate Limiting
    RATELIMIT_REQUESTS = int(os.environ.get('RATELIMIT_REQUESTS', 100))
    RATELIMIT_WINDOW = int(os.environ.get('RATELIMIT_WINDOW', 3600))  # seconds
    
    # LLM timeouts (seconds)
    LLM_TIMEOUT = int(os.environ.get('LLM_TIMEOUT', 30))
    LLM_MAX_RETRIES = int(os.environ.get('LLM_MAX_RETRIES', 2))
    
    @classmethod
    def validate_production(cls):
        """Raise exceptions if critical config is missing in production."""
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'dev-secret-key-change-in-prod':
            raise ValueError("SECRET_KEY must be set in production")
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required for Planner agent")
        # HF token is optional for production (if you use HF models)
        # but we'll warn if missing and HF models are configured
        return True


class DevConfig(Config):
    """Development environment - debug enabled, local database."""
    DEBUG = True
    ENV = 'development'


class ProdConfig(Config):
    """Production environment - strict validation, debug off."""
    DEBUG = False
    ENV = 'production'
    
    def __init__(self):
        self.validate_production()


# Dictionary for easy selection
config_by_name = {
    'dev': DevConfig,
    'prod': ProdConfig
}
