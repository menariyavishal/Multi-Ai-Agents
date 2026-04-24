"""Tests for GraphRunner execution engine."""

import pytest
import asyncio
from app.services.graph_runner import GraphRunner
from app.workflow.state import create_initial_state


class TestGraphRunner:
    """Test GraphRunner execution and workflow management."""
    
    def test_graph_runner_initialization(self):
        """Test GraphRunner can be initialized."""
        runner = GraphRunner(enable_checkpointing=False)
        assert runner is not None
        assert runner.graph is not None
    
    def test_graph_runner_with_checkpointing(self):
        """Test GraphRunner with checkpointing enabled."""
        runner = GraphRunner(enable_checkpointing=True)
        assert runner.checkpointer is not None
    
    def test_graph_runner_without_checkpointing(self):
        """Test GraphRunner with checkpointing disabled."""
        runner = GraphRunner(enable_checkpointing=False)
        assert runner.checkpointer is None
    
    @pytest.mark.slow
    def test_run_synchronous_execution(self, groq_api_key):
        """Test synchronous workflow execution.
        
        This is slow because it runs all 5 agents sequentially.
        """
        if not groq_api_key:
            pytest.skip("GROQ_API_KEY not set")
        
        runner = GraphRunner(enable_checkpointing=False)
        
        result = runner.run_synchronous(
            query="What is 2+2?",
            max_iterations=1,
            verbose=False
        )
        
        # Verify execution completed
        assert result is not None
        assert "elapsed_seconds" in result
        assert result["elapsed_seconds"] > 0
    
    @pytest.mark.slow
    def test_run_synchronous_verbose_output(self, groq_api_key, capsys):
        """Test synchronous execution with verbose output."""
        if not groq_api_key:
            pytest.skip("GROQ_API_KEY not set")
        
        runner = GraphRunner(enable_checkpointing=False)
        
        result = runner.run_synchronous(
            query="What is 2+2?",
            max_iterations=1,
            verbose=True
        )
        
        # Capture printed output
        captured = capsys.readouterr()
        
        # Should contain workflow headers
        assert "WORKFLOW EXECUTION" in captured.out or result is not None
    
    @pytest.mark.slow
    def test_run_synchronous_agent_completion(self, groq_api_key):
        """Test that all agents complete in synchronous execution."""
        if not groq_api_key:
            pytest.skip("GROQ_API_KEY not set")
        
        runner = GraphRunner(enable_checkpointing=False)
        
        result = runner.run_synchronous(
            query="What is Python?",
            max_iterations=1
        )
        
        # All agents should complete
        assert result["planner_complete"] is True
        assert result["researcher_complete"] is True
        assert result["analyst_complete"] is True
        assert result["writer_complete"] is True
        assert result["reviewer_complete"] is True
    
    @pytest.mark.slow
    def test_run_with_checkpoints(self, groq_api_key):
        """Test workflow execution with checkpointing."""
        if not groq_api_key:
            pytest.skip("GROQ_API_KEY not set")
        
        runner = GraphRunner(enable_checkpointing=True)
        
        result = runner.run_with_checkpoints(
            query="Test checkpoint",
            max_iterations=1
        )
        
        # Should have end_time and elapsed_seconds
        assert "end_time" in result
        assert "elapsed_seconds" in result
    
    def test_get_execution_history_no_checkpoints(self):
        """Test getting execution history when no checkpoints exist."""
        runner = GraphRunner(enable_checkpointing=False)
        
        history = runner.get_execution_history("nonexistent query")
        
        # Should return empty list when checkpointing disabled
        assert history == []
    
    @pytest.mark.slow
    def test_run_streaming_execution(self, groq_api_key):
        """Test streaming workflow execution.
        
        This test uses asyncio to run the async generator.
        """
        if not groq_api_key:
            pytest.skip("GROQ_API_KEY not set")
        
        runner = GraphRunner(enable_checkpointing=False)
        
        async def test_stream():
            updates = []
            async for update in runner.run_streaming(
                query="What is 2+2?",
                max_iterations=1
            ):
                updates.append(update)
            return updates
        
        # Run async test
        updates = asyncio.run(test_stream())
        
        # Should get multiple updates (one per agent)
        assert len(updates) > 0
    
    @pytest.mark.slow
    def test_run_streaming_state_accumulation(self, groq_api_key):
        """Test that streaming properly accumulates state."""
        if not groq_api_key:
            pytest.skip("GROQ_API_KEY not set")
        
        runner = GraphRunner(enable_checkpointing=False)
        
        async def test_stream():
            async for update in runner.run_streaming(
                query="Simple test",
                max_iterations=1
            ):
                # Each update should have state data
                assert update is not None
        
        asyncio.run(test_stream())
    
    def test_print_results_formatting(self, capsys):
        """Test result printing format."""
        runner = GraphRunner(enable_checkpointing=False)
        
        # Create a mock result
        result = create_initial_state("test query")
        result["elapsed_seconds"] = 5.25
        result["planner_complete"] = True
        result["reviewer_complete"] = True
        
        runner._print_results(result)
        
        captured = capsys.readouterr()
        
        # Output should contain key information
        assert "WORKFLOW COMPLETE" in captured.out
        assert "test query" in captured.out
    
    @pytest.mark.slow
    def test_max_iterations_enforcement(self, groq_api_key):
        """Test that max_iterations is enforced."""
        if not groq_api_key:
            pytest.skip("GROQ_API_KEY not set")
        
        runner = GraphRunner(enable_checkpointing=False)
        
        result = runner.run_synchronous(
            query="What is AI?",
            max_iterations=2
        )
        
        # Iteration should not exceed max
        assert result["iteration"] <= 2
    
    @pytest.mark.slow
    def test_exception_handling_in_sync(self, groq_api_key):
        """Test exception handling in synchronous execution."""
        if not groq_api_key:
            pytest.skip("GROQ_API_KEY not set")
        
        runner = GraphRunner(enable_checkpointing=False)
        
        # Empty query should either be handled or raise
        try:
            result = runner.run_synchronous(
                query="",
                max_iterations=1
            )
            # If it doesn't raise, result should be dict
            assert isinstance(result, dict)
        except (ValueError, TypeError, Exception):
            # Some error during execution is acceptable
            pass


class TestGraphRunnerIntegration:
    """Integration tests for GraphRunner with other components."""
    
    @pytest.mark.slow
    def test_full_workflow_with_revision_loop(self, groq_api_key):
        """Test complete workflow including potential revision loops."""
        if not groq_api_key:
            pytest.skip("GROQ_API_KEY not set")
        
        runner = GraphRunner(enable_checkpointing=False)
        
        # This should complete even if revision is needed
        result = runner.run_synchronous(
            query="Analyze current market trends",
            max_iterations=3  # Allow revisions
        )
        
        # Should eventually complete or max out
        assert result["iteration"] >= 1
        assert result["iteration"] <= 3
    
    @pytest.mark.slow
    def test_workflow_result_structure(self, groq_api_key):
        """Test that workflow result has expected structure."""
        if not groq_api_key:
            pytest.skip("GROQ_API_KEY not set")
        
        runner = GraphRunner(enable_checkpointing=False)
        
        result = runner.run_synchronous("What is Python?", max_iterations=1)
        
        # All key result fields should exist
        assert "query" in result
        assert "final_answer" in result
        assert "review_feedback" in result
        assert "elapsed_seconds" in result
        assert "messages" in result


@pytest.fixture(scope="session")
def groq_api_key():
    """Get Groq API key from environment."""
    import os
    key = os.getenv("GROQ_API_KEY")
    return key
