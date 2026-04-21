"""Conditional routing logic for LangGraph workflow edges."""

from typing import Any, Dict
from app.workflow.state import WorkflowState
from app.core.logger import get_logger

logger = get_logger(__name__)


def route_from_planner(state: WorkflowState) -> str:
    """Route from Planner to next agent.
    
    Args:
        state: Current workflow state
    
    Returns:
        Next agent name ('researcher')
    """
    logger.info("Routing: Planner → Researcher")
    return "researcher"


def route_from_researcher(state: WorkflowState) -> str:
    """Route from Researcher to next agent.
    
    Args:
        state: Current workflow state
    
    Returns:
        Next agent name ('analyst')
    """
    logger.info("Routing: Researcher → Analyst")
    return "analyst"


def route_from_analyst(state: WorkflowState) -> str:
    """Route from Analyst to next agent.
    
    Args:
        state: Current workflow state
    
    Returns:
        Next agent name ('writer')
    """
    logger.info("Routing: Analyst → Writer")
    return "writer"


def route_from_writer(state: WorkflowState) -> str:
    """Route from Writer to next agent.
    
    Args:
        state: Current workflow state
    
    Returns:
        Next agent name ('reviewer')
    """
    logger.info("Routing: Writer → Reviewer")
    return "reviewer"


def route_from_reviewer(state: WorkflowState) -> str:
    """Route from Reviewer based on quality decision.
    
    This is the critical routing decision that controls workflow flow:
    - If PASS: Go to END (delivery)
    - If NEEDS_REVISION: Loop back to Writer for improvements
    - If max iterations reached: Force END regardless
    
    Args:
        state: Current workflow state
    
    Returns:
        Next node ('end' or 'writer')
    """
    routing_decision = state.get("routing_decision", "").upper()
    iteration = state.get("iteration", 1)
    max_iterations = state.get("max_iterations", 3)
    
    # Check iteration limit first
    if iteration >= max_iterations:
        logger.warning(f"Max iterations ({max_iterations}) reached, forcing END")
        return "end"
    
    # Check reviewer decision
    if routing_decision == "PASS":
        logger.info("Reviewer PASSED - proceeding to END")
        return "end"
    elif routing_decision == "NEEDS_REVISION":
        logger.info(f"Reviewer requested revision (iteration {iteration}/{max_iterations}) - looping to Writer")
        return "writer"
    else:
        # Unknown state, default to END with warning
        logger.warning(f"Unknown routing decision '{routing_decision}', defaulting to END")
        return "end"


def should_continue(state: WorkflowState) -> bool:
    """Determine if workflow should continue.
    
    Args:
        state: Current workflow state
    
    Returns:
        True if should continue, False if should end
    """
    iteration = state.get("iteration", 1)
    max_iterations = state.get("max_iterations", 3)
    reviewer_complete = state.get("reviewer_complete", False)
    
    # Stop if reviewer complete and approved
    if reviewer_complete and state.get("routing_decision", "").upper() == "PASS":
        return False
    
    # Stop if max iterations reached
    if iteration >= max_iterations:
        return False
    
    # Continue otherwise
    return True
