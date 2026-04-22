"""Workflow manager - High-level API for orchestrating multi-agent system."""

from typing import Any, Dict, Optional, AsyncGenerator
from app.services.graph_runner import GraphRunner
from app.workflow.state import WorkflowState
from app.core.logger import get_logger

logger = get_logger(__name__)


class WorkflowManager:
    """High-level manager for multi-agent workflow execution."""
    
    def __init__(self, enable_checkpointing: bool = True):
        """Initialize workflow manager.
        
        Args:
            enable_checkpointing: Whether to enable checkpoint persistence
        """
        self.runner = GraphRunner(enable_checkpointing=enable_checkpointing)
        logger.info("WorkflowManager initialized")
    
    def process_query(
        self,
        query: str,
        user_id: str = "",
        max_iterations: int = 3,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """Process user query through complete 5-agent workflow.
        
        Synchronous execution - blocks until complete.
        
        Args:
            query: User question or request
            user_id: User identifier for database context and conversation history
            max_iterations: Maximum revision cycles allowed (1-5, default 3)
            verbose: Print detailed execution info
        
        Returns:
            Workflow result with final_answer if approved, else feedback
        
        Example:
            >>> manager = WorkflowManager()
            >>> result = manager.process_query("What are AI trends?", user_id="user123")
            >>> if result['final_answer']:
            ...     print(result['final_answer'])
            ... else:
            ...     print(result['review_feedback'])
        """
        logger.info(f"Processing query: {query[:80]} for user: {user_id}")
        
        # Validate max_iterations
        max_iterations = max(1, min(5, max_iterations))
        
        # Run synchronous workflow
        return self.runner.run_synchronous(
            query=query,
            user_id=user_id,
            max_iterations=max_iterations,
            verbose=verbose
        )
    
    def process_query_streaming(
        self,
        query: str,
        max_iterations: int = 3
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Process query with streaming output (async).
        
        Yields updates as each agent completes.
        
        Args:
            query: User question or request
            max_iterations: Maximum revision cycles allowed
        
        Yields:
            Updated state after each agent completes
        
        Example:
            >>> manager = WorkflowManager()
            >>> async for update in manager.process_query_streaming("What are AI trends?"):
            ...     print(f"Agent complete: {update}")
        """
        logger.info(f"Starting streaming workflow for: {query[:80]}")
        
        max_iterations = max(1, min(5, max_iterations))
        
        # Return async generator
        return self.runner.run_streaming(
            query=query,
            max_iterations=max_iterations
        )
    
    def get_result_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key information from workflow result.
        
        Args:
            result: Complete workflow state
        
        Returns:
            Simplified summary for API response
        """
        review_feedback = result.get("review_feedback", {})
        analysis = result.get("analysis", {})
        
        return {
            "query": result.get("query", ""),
            "status": "approved" if result.get("final_answer") else "needs_revision",
            "iterations_used": result.get("iteration", 1),
            "execution_time_seconds": result.get("elapsed_seconds", 0),
            
            "plan": result.get("plan", "")[:200],  # Truncate for preview
            "research_summary": result.get("research", "")[:200],
            
            "analysis": {
                "patterns_count": len(analysis.get("patterns", [])),
                "insights_count": len(analysis.get("insights", [])),
                "recommendations_count": len(analysis.get("recommendations", [])),
                "confidence_level": analysis.get("confidence_level", 0),
                "data_quality": analysis.get("data_quality", "unknown")
            },
            
            "review": {
                "quality_score": review_feedback.get("quality_score", 0),
                "quality_level": review_feedback.get("quality_level", "unknown"),
                "recommendation": review_feedback.get("recommendation", "unknown"),
                "total_issues": review_feedback.get("total_issues", 0)
            },
            
            "final_answer": result.get("final_answer", ""),
            
            "agent_completion": {
                "planner": result.get("planner_complete", False),
                "researcher": result.get("researcher_complete", False),
                "analyst": result.get("analyst_complete", False),
                "writer": result.get("writer_complete", False),
                "reviewer": result.get("reviewer_complete", False)
            }
        }
    
    def get_execution_history(self, query: str) -> list:
        """Get execution history (checkpoints) for a query.
        
        Args:
            query: User query to get history for
        
        Returns:
            List of checkpoint file paths
        """
        return self.runner.get_execution_history(query)
    
    def recover_from_checkpoint(
        self,
        checkpoint_path: str,
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """Resume workflow from a saved checkpoint.
        
        Args:
            checkpoint_path: Path to checkpoint file
            max_iterations: Maximum iterations for resumed workflow
        
        Returns:
            Final workflow result
        """
        logger.info(f"Recovering from checkpoint: {checkpoint_path}")
        
        return self.runner.run_with_checkpoints(
            query="recovered",
            resume_from=checkpoint_path,
            max_iterations=max_iterations
        )


# Global instance for use across application
_workflow_manager: Optional[WorkflowManager] = None


def get_workflow_manager(
    enable_checkpointing: bool = True
) -> WorkflowManager:
    """Get or create global WorkflowManager instance.
    
    Args:
        enable_checkpointing: Whether to enable checkpointing
    
    Returns:
        Global WorkflowManager instance
    """
    global _workflow_manager
    
    if _workflow_manager is None:
        _workflow_manager = WorkflowManager(enable_checkpointing=enable_checkpointing)
    
    return _workflow_manager
