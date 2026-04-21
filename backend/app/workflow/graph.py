"""LangGraph workflow builder - orchestrates 5-agent system."""

from typing import Any, Dict, cast
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.workflow.state import WorkflowState
from app.workflow.edges import (
    route_from_planner, route_from_researcher, route_from_analyst,
    route_from_writer, route_from_reviewer
)
from app.agents.planner import Planner
from app.agents.researcher import Researcher
from app.agents.analyst import Analyst
from app.agents.writer import Writer
from app.agents.reviewer import Reviewer
from app.core.logger import get_logger

logger = get_logger(__name__)


def build_workflow_graph() -> CompiledStateGraph:
    """Build the complete 5-agent workflow graph with revision loop.
    
    Graph structure:
    START → Planner → Researcher → Analyst → Writer → Reviewer → END
                                                          ↓
                                                    [NEEDS_REVISION]
                                                          ↓
                                                      Writer (cycle)
    
    Returns:
        Compiled StateGraph ready for execution
    """
    
    # Initialize agents (singleton instances)
    planner = Planner()
    researcher = Researcher()
    analyst = Analyst()
    writer = Writer()
    reviewer = Reviewer()
    
    logger.info("Initializing 5-agent workflow graph")
    
    # Create graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes (agent functions)
    workflow.add_node("planner", _planner_node(planner))
    workflow.add_node("researcher", _researcher_node(researcher))
    workflow.add_node("analyst", _analyst_node(analyst))
    workflow.add_node("writer", _writer_node(writer))
    workflow.add_node("reviewer", _reviewer_node(reviewer))
    
    # Add edges (linear flow)
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "analyst")
    workflow.add_edge("analyst", "writer")
    workflow.add_edge("writer", "reviewer")
    
    # Add conditional edge from reviewer (routing decision)
    workflow.add_conditional_edges(
        "reviewer",
        route_from_reviewer,
        {
            "end": END,
            "writer": "writer"  # Loop back for revision
        }
    )
    
    # Set entry point
    workflow.set_entry_point("planner")
    
    logger.info("Workflow graph constructed successfully")
    
    return workflow.compile()


def _planner_node(planner: Planner):
    """Create Planner node function for StateGraph.
    
    Args:
        planner: Planner agent instance
    
    Returns:
        Node function that updates state
    """
    def planner_wrapper(state: WorkflowState) -> Dict[str, Any]:
        """Execute Planner and update state."""
        logger.info("Executing Planner node")
        result = planner.call(cast(Dict[str, Any], state))
        
        return {
            "plan": result.get("plan", ""),
            "planner_complete": result.get("planner_complete", False),
            "messages": result.get("messages", []),
            "iteration": state.get("iteration", 1)
        }
    
    return planner_wrapper


def _researcher_node(researcher: Researcher):
    """Create Researcher node function for StateGraph.
    
    Args:
        researcher: Researcher agent instance
    
    Returns:
        Node function that updates state
    """
    def researcher_wrapper(state: WorkflowState) -> Dict[str, Any]:
        """Execute Researcher and update state."""
        logger.info("Executing Researcher node")
        result = researcher.call(cast(Dict[str, Any], state))
        
        return {
            "research": result.get("research", ""),
            "researcher_complete": result.get("researcher_complete", False),
            "messages": result.get("messages", [])
        }
    
    return researcher_wrapper


def _analyst_node(analyst: Analyst):
    """Create Analyst node function for StateGraph.
    
    Args:
        analyst: Analyst agent instance
    
    Returns:
        Node function that updates state
    """
    def analyst_wrapper(state: WorkflowState) -> Dict[str, Any]:
        """Execute Analyst and update state."""
        logger.info("Executing Analyst node")
        result = analyst.call(cast(Dict[str, Any], state))
        
        return {
            "analysis": result.get("analysis", {}),
            "analyst_complete": result.get("analyst_complete", False),
            "messages": result.get("messages", [])
        }
    
    return analyst_wrapper


def _writer_node(writer: Writer):
    """Create Writer node function for StateGraph.
    
    Args:
        writer: Writer agent instance
    
    Returns:
        Node function that updates state
    """
    def writer_wrapper(state: WorkflowState) -> Dict[str, Any]:
        """Execute Writer and update state."""
        logger.info("Executing Writer node")
        result = writer.call(cast(Dict[str, Any], state))
        
        # Increment iteration if this is a revision cycle
        iteration = state.get("iteration", 1)
        if state.get("writer_complete"):  # If Writer was already complete, this is revision
            iteration += 1
        
        return {
            "draft": result.get("draft", ""),
            "writer_complete": result.get("writer_complete", False),
            "messages": result.get("messages", []),
            "iteration": iteration
        }
    
    return writer_wrapper


def _reviewer_node(reviewer: Reviewer):
    """Create Reviewer node function for StateGraph.
    
    Args:
        reviewer: Reviewer agent instance
    
    Returns:
        Node function that updates state
    """
    def reviewer_wrapper(state: WorkflowState) -> Dict[str, Any]:
        """Execute Reviewer and update state."""
        logger.info("Executing Reviewer node")
        result = reviewer.call(cast(Dict[str, Any], state))
        
        review_feedback = result.get("review_feedback", {})
        routing_decision = review_feedback.get("recommendation", "NEEDS_REVISION")
        
        return {
            "review_feedback": review_feedback,
            "reviewer_complete": result.get("reviewer_complete", False),
            "final_answer": result.get("final_answer", ""),
            "routing_decision": routing_decision,
            "messages": result.get("messages", [])
        }
    
    return reviewer_wrapper
