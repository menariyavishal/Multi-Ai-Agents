"""Integration tests for Groq API."""

import pytest
from langchain_groq import ChatGroq


class TestGroqAPI:
    """Test suite for Groq API integration."""

    def test_groq_api_initialization(self, groq_api_key):
        """Test that Groq LLM can be initialized with API key."""
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=groq_api_key
        )
        assert llm is not None
        assert llm.model_name == "llama-3.3-70b-versatile"

    def test_groq_api_invoke(self, groq_api_key):
        """Test that Groq API can invoke a query successfully."""
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=groq_api_key
        )
        
        query = "Create a 3-step plan for learning AI"
        response = llm.invoke(query)
        
        assert response is not None
        assert hasattr(response, 'content')
        assert len(response.content) > 0
        assert "step" in response.content.lower() or "plan" in response.content.lower()

    def test_groq_api_response_quality(self, groq_api_key):
        """Test that Groq API returns meaningful responses."""
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=groq_api_key
        )
        
        query = "What is machine learning?"
        response = llm.invoke(query)
        
        assert response is not None
        assert len(response.content) > 50  # Should be a substantial response
        assert isinstance(response.content, str)
