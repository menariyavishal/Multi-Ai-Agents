"""Tests for Planner agent with Groq API."""

import os
import sys
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.llm_factory import LLMFactory


class TestPlannerAgent:
    """Test suite for Planner agent with Groq LLM."""

    def test_llm_factory_creates_groq_for_planner(self, groq_api_key):
        """Test that LLMFactory creates Groq LLM for planner role."""
        # Clear cache to ensure fresh instance
        LLMFactory.clear_cache()
        
        llm = LLMFactory.get_llm("planner")
        
        assert llm is not None
        # Verify it's a Groq LLM by checking the class name
        assert "Groq" in type(llm).__name__ or hasattr(llm, 'model_name')

    def test_planner_llm_invoke(self, groq_api_key):
        """Test that Planner LLM can invoke queries successfully."""
        LLMFactory.clear_cache()
        
        planner_llm = LLMFactory.get_llm("planner")
        
        query = "Create a comprehensive plan for building a weather forecasting AI system"
        response = planner_llm.invoke(query)
        
        assert response is not None
        assert hasattr(response, 'content')
        assert len(response.content) > 0

    def test_planner_llm_generates_structured_plan(self, groq_api_key):
        """Test that Planner LLM generates structured, meaningful plans."""
        LLMFactory.clear_cache()
        
        planner_llm = LLMFactory.get_llm("planner")
        
        query = "Create a plan for implementing microservices architecture"
        response = planner_llm.invoke(query)
        
        content = response.content
        
        # Verify response contains planning-related elements
        planning_keywords = ['step', 'plan', 'phase', 'stage', 'component', 'module', '1.', '2.', '3.']
        has_planning_keywords = any(keyword.lower() in content.lower() for keyword in planning_keywords)
        
        assert has_planning_keywords, "Response should contain planning-related content"
        assert len(content) > 100, "Response should be substantial"

    def test_planner_llm_temperature_setting(self, groq_api_key):
        """Test that Planner LLM has correct temperature for planning."""
        LLMFactory.clear_cache()
        
        llm = LLMFactory.get_llm("planner")
        
        # Planner should have lower temperature (more deterministic)
        # Check from constants
        from app.core.constants import MODEL_CONFIGS
        assert MODEL_CONFIGS["planner"]["temperature"] == 0.3
        assert MODEL_CONFIGS["planner"]["provider"] == "groq"

    def test_planner_llm_caching(self, groq_api_key):
        """Test that LLMFactory caches LLM instances properly."""
        LLMFactory.clear_cache()
        
        llm1 = LLMFactory.get_llm("planner")
        llm2 = LLMFactory.get_llm("planner")
        
        # Should return the same instance (cached)
        assert llm1 is llm2
