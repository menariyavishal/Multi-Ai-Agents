"""Integration tests for Planner Agent implementation."""

import pytest
from app.agents.planner import Planner


class TestPlannerAgentImplementation:
    """Test suite for actual Planner agent implementation."""

    def test_planner_initialization(self):
        """Test that Planner agent initializes correctly."""
        planner = Planner()
        
        assert planner is not None
        assert planner.agent_role == "planner"
        assert planner.llm is not None

    def test_planner_call_with_query(self):
        """Test Planner agent processes a query and returns plan."""
        planner = Planner()
        
        state = {
            "query": "Build a weather forecasting AI system",
            "iteration": 1
        }
        
        result = planner.call(state)
        
        assert result is not None
        assert "plan" in result
        assert result["planner_complete"] is True
        assert len(result["plan"]) > 0
        assert result["plan"] != "No query provided"

    def test_planner_call_with_context(self):
        """Test Planner agent with additional context."""
        planner = Planner()
        
        state = {
            "query": "Design a microservices architecture",
            "context": "Using Python and Docker",
            "iteration": 1
        }
        
        result = planner.call(state)
        
        assert result is not None
        assert result["planner_complete"] is True
        assert "plan" in result
        assert len(result["plan"]) > 0

    def test_planner_call_without_query(self):
        """Test Planner agent handles missing query gracefully."""
        planner = Planner()
        
        state = {"iteration": 1}
        
        result = planner.call(state)
        
        assert result is not None
        assert result["planner_complete"] is True
        assert "plan" in result
        # Should return graceful error message
        assert "No query provided" in result["plan"] or len(result["plan"]) > 0

    def test_planner_plan_contains_planning_elements(self):
        """Test that generated plan contains expected planning elements."""
        planner = Planner()
        
        state = {
            "query": "Create a deployment strategy for a web application",
            "iteration": 1
        }
        
        result = planner.call(state)
        plan = result["plan"].lower()
        
        # Plan should contain some planning-related elements
        planning_keywords = ['objective', 'step', 'phase', 'resource', 'timeline', 
                            'risk', 'metric', 'goal', 'plan', 'stage']
        has_keywords = any(keyword in plan for keyword in planning_keywords)
        
        assert has_keywords, "Plan should contain planning-related elements"

    def test_planner_state_passthrough(self):
        """Test that Planner preserves existing state values."""
        planner = Planner()
        
        initial_state = {
            "query": "Test query",
            "iteration": 2,
            "user_id": "user123",
            "custom_field": "custom_value"
        }
        
        result = planner.call(initial_state)
        
        # Original fields should be preserved
        assert result["iteration"] == 2
        assert result["user_id"] == "user123"
        assert result["custom_field"] == "custom_value"
        # New fields should be added
        assert "plan" in result
        assert "planner_complete" in result

    def test_planner_messages_tracking(self):
        """Test that Planner tracks messages in state."""
        planner = Planner()
        
        state = {
            "query": "Sample query",
            "iteration": 1,
            "messages": []
        }
        
        result = planner.call(state)
        
        assert "messages" in result
        assert isinstance(result["messages"], list)
        # Should have added a message
        assert len(result["messages"]) >= 1
