"""Workflow state definition using TypedDict for LangGraph."""

from typing import Any, Dict, List, TypedDict


class WorkflowState(TypedDict, total=False):
    """Complete state for 5-agent workflow.
    
    total=False allows optional fields. All fields are technically present but
    may be None/empty until an agent populates them.
    """
    
    # Input
    query: str
    """Original user query that starts the workflow."""
    
    iteration: int
    """Current iteration count for tracking cycles (revision loops)."""
    
    max_iterations: int
    """Maximum iterations allowed before terminating workflow."""
    
    # Agent outputs
    plan: str
    """Planner agent output - detailed execution plan."""
    
    research: str
    """Researcher agent output - gathered research findings."""
    
    analysis: Dict[str, Any]
    """Analyst agent output - patterns, insights, recommendations."""
    
    draft: str
    """Writer agent output - polished written report."""
    
    review_feedback: Dict[str, Any]
    """Reviewer agent output - quality assessment and feedback."""
    
    # Completion flags
    planner_complete: bool
    """Whether Planner agent has completed execution."""
    
    researcher_complete: bool
    """Whether Researcher agent has completed execution."""
    
    analyst_complete: bool
    """Whether Analyst agent has completed execution."""
    
    writer_complete: bool
    """Whether Writer agent has completed execution."""
    
    reviewer_complete: bool
    """Whether Reviewer agent has completed execution."""
    
    # Routing
    next_agent: str
    """Which agent should execute next (routing decision)."""
    
    routing_decision: str
    """Reviewer's decision: 'PASS' or 'NEEDS_REVISION'."""
    
    final_answer: str
    """Final approved output ready for delivery to user."""
    
    # Messages
    messages: List[Dict[str, str]]
    """Conversation history with role/content format."""
    
    # Metadata
    start_time: float
    """Unix timestamp when workflow started."""
    
    end_time: float
    """Unix timestamp when workflow ended."""
    
    elapsed_seconds: float
    """Total execution time in seconds."""


def create_initial_state(query: str, max_iterations: int = 3) -> WorkflowState:
    """Create initial workflow state from user query.
    
    Args:
        query: The user's question/request
        max_iterations: Maximum revision cycles allowed (default 3)
    
    Returns:
        Initialized WorkflowState ready for first agent
    """
    import time
    
    return WorkflowState(
        query=query,
        iteration=1,
        max_iterations=max_iterations,
        plan="",
        research="",
        analysis={},
        draft="",
        review_feedback={},
        planner_complete=False,
        researcher_complete=False,
        analyst_complete=False,
        writer_complete=False,
        reviewer_complete=False,
        next_agent="planner",
        routing_decision="",
        final_answer="",
        messages=[],
        start_time=time.time(),
        end_time=0.0,
        elapsed_seconds=0.0
    )
