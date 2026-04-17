"""Pytest configuration and shared fixtures for tests."""

import os
import pytest
from dotenv import load_dotenv

# Load environment variables before tests
load_dotenv()


@pytest.fixture
def groq_api_key():
    """Fixture to provide Groq API key from environment."""
    key = os.getenv('GROQ_API_KEY')
    if not key:
        pytest.skip("GROQ_API_KEY not set in environment")
    return key


@pytest.fixture
def hf_api_token():
    """Fixture to provide HuggingFace API token from environment."""
    token = os.getenv('HF_API_TOKEN')
    if not token:
        pytest.skip("HF_API_TOKEN not set in environment")
    return token


@pytest.fixture
def mongodb_uri():
    """Fixture to provide MongoDB URI from environment."""
    uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/multi_ai_agents')
    return uri
