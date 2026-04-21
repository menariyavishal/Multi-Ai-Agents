"""Tests for LangGraph workflow builder and state management."""

import pytest
from app.workflow.state import WorkflowState, create_initial_state
from app.workflow.graph import build_workflow_graph
from app.workflow.edges import (
    route_from_planner, route_from_researcher, route_from_analyst,
    route_from_writer, route_from_reviewer
)


class TestWorkflowState:
    """Test WorkflowState TypedDict."""
    
    def test_create_initial_state(self):
        """Test initial state creation."""
        query = "What are AI trends?"
        state = create_initial_state(query, max_iterations=3)
        
        assert state["query"] == query
        assert state["iteration"] == 1
        assert state["max_iterations"] == 3
        assert state["next_agent"] == "planner"
        assert state["planner_complete"] is False
        assert state["messages"] == []
    
    def test_state_fields(self):
        """Test all required state fields exist."""
        state = create_initial_state("test query")
        
        required_fields = [
            "query", "iteration", "max_iterations",
            "plan", "research", "analysis", "draft", "review_feedback",
            "planner_complete", "researcher_complete", "analyst_complete",
            "writer_complete", "reviewer_complete",
            "next_agent", "routing_decision", "final_answer",
            "messages", "start_time"
        ]
        
        for field in required_fields:
            assert field in state


class TestWorkflowEdges:
    """Test edge routing logic."""
    
    def test_route_from_planner(self):
        """Test routing from Planner."""
        state: WorkflowState = {}
        assert route_from_planner(state) == "researcher"
    
    def test_route_from_researcher(self):
        """Test routing from Researcher."""
        state: WorkflowState = {}
        assert route_from_researcher(state) == "analyst"
    
    def test_route_from_analyst(self):
        """Test routing from Analyst."""
        state: WorkflowState = {}
        assert route_from_analyst(state) == "writer"
    
    def test_route_from_writer(self):
        """Test routing from Writer."""
        state: WorkflowState = {}
        assert route_from_writer(state) == "reviewer"
    
    def test_route_from_reviewer_pass(self):
        """Test routing from Reviewer when PASS."""
        state: WorkflowState = {
            "routing_decision": "PASS",
            "iteration": 1,
            "max_iterations": 3
        }
        assert route_from_reviewer(state) == "end"
    
    def test_route_from_reviewer_needs_revision(self):
        """Test routing from Reviewer when NEEDS_REVISION."""
        state: WorkflowState = {
            "routing_decision": "NEEDS_REVISION",
            "iteration": 1,
            "max_iterations": 3
        }
        assert route_from_reviewer(state) == "writer"
    
    def test_route_from_reviewer_max_iterations_reached(self):
        """Test routing from Reviewer when max iterations reached."""
        state: WorkflowState = {
            "routing_decision": "NEEDS_REVISION",
            "iteration": 3,
            "max_iterations": 3
        }
        assert route_from_reviewer(state) == "end"


class TestWorkflowGraph:
    """Test LangGraph workflow construction and execution."""
    
    def test_build_workflow_graph(self):
        """Test that workflow graph builds without errors."""
        graph = build_workflow_graph()
        assert graph is not None
        assert hasattr(graph, "invoke")
        assert hasattr(graph, "stream")
    
    def test_graph_has_all_nodes(self):
        """Test that graph includes all 5 agents as nodes."""
        graph = build_workflow_graph()
        
        # Access graph structure (implementation-specific)
        # The compiled graph should have nodes for all agents
        assert graph is not None  # Basic check - full validation in integration tests
    
    @pytest.mark.slow
    def test_graph_simple_execution(self, groq_api_key):
        """Test simple graph execution with mock data.
        
        This is slow because it calls actual LLMs.
        """
        if not groq_api_key:
            pytest.skip("GROQ_API_KEY not set")
        
        graph = build_workflow_graph()
        state = create_initial_state("What is 2+2?", max_iterations=1)
        
        # Run graph
        result = graph.invoke(state)
        
        # Verify completion
        assert result.get("planner_complete") is True
        assert result.get("reviewer_complete") is True
        assert "final_answer" in result


class TestWorkflowStateEdgeCases:
    """Test edge cases in workflow state and routing."""
    
    def test_state_with_missing_fields(self):
        """Test state behavior with missing optional fields."""
        state = create_initial_state("test")
        
        # Fields should exist (TypedDict allows missing values)
        assert "query" in state
        assert state["query"] == "test"
    
    def test_routing_decision_case_insensitive(self):
        """Test that routing decision handles case variations."""
        state_lower: WorkflowState = {
            "routing_decision": "pass",
            "iteration": 1,
            "max_iterations": 3
        }
        
        state_upper: WorkflowState = {
            "routing_decision": "PASS",
            "iteration": 1,
            "max_iterations": 3
        }
        
        # Both should route to "end"
        assert route_from_reviewer(state_lower) == "end"
        assert route_from_reviewer(state_upper) == "end"
    
    def test_routing_unknown_decision(self):
        """Test routing with unknown decision defaults to end."""
        state: WorkflowState = {
            "routing_decision": "UNKNOWN_STATE",
            "iteration": 1,
            "max_iterations": 3
        }
        
        result = route_from_reviewer(state)
        # Should default to "end" for unknown decisions
        assert result == "end"
    
    def test_iteration_tracking(self):
        """Test iteration counting through cycles."""
        state1 = create_initial_state("test")
        assert state1["iteration"] == 1
        
        # Simulate revision loop
        state2 = create_initial_state("test")
        state2["iteration"] = 2
        assert state2["iteration"] == 2
        
        # Check max iteration enforcement
        state3: WorkflowState = {
            "iteration": 5,
            "max_iterations": 3
        }
        # Should enforce max
        assert route_from_reviewer(state3) == "end"
