"""Graph execution engine - runs compiled LangGraph workflow."""

import time
import asyncio
from typing import Any, Dict, AsyncGenerator, Optional
from app.workflow.state import WorkflowState, create_initial_state
from app.workflow.graph import build_workflow_graph
from app.workflow.checkpointer import WorkflowCheckpointer
from app.core.logger import get_logger

logger = get_logger(__name__)


class GraphRunner:
    """Executes the compiled LangGraph workflow with streaming support."""
    
    def __init__(self, enable_checkpointing: bool = True):
        """Initialize graph runner.
        
        Args:
            enable_checkpointing: Whether to save checkpoints at each step
        """
        self.graph = build_workflow_graph()
        self.checkpointer = WorkflowCheckpointer() if enable_checkpointing else None
        logger.info("GraphRunner initialized")
    
    def run_synchronous(
        self,
        query: str,
        max_iterations: int = 3,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """Run workflow synchronously (blocking).
        
        Args:
            query: User query to process
            max_iterations: Maximum revision cycles (default 3)
            verbose: Print detailed logging
        
        Returns:
            Final workflow state
        """
        logger.info(f"Starting synchronous workflow for query: {query[:100]}")
        
        # Create initial state
        state = create_initial_state(query, max_iterations)
        
        if verbose:
            print(f"\n{'='*80}")
            print(f"WORKFLOW EXECUTION: {query}")
            print(f"{'='*80}\n")
        
        try:
            # Execute graph
            result = self.graph.invoke(state)
            
            # Record end time
            result["end_time"] = time.time()
            result["elapsed_seconds"] = result["end_time"] - result["start_time"]
            
            if verbose:
                self._print_results(result)
            
            logger.info(f"Workflow completed in {result['elapsed_seconds']:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            raise
    
    async def run_streaming(
        self,
        query: str,
        max_iterations: int = 3
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Run workflow with streaming output (async generator).
        
        Yields state updates as each agent completes.
        
        Args:
            query: User query to process
            max_iterations: Maximum revision cycles
        
        Yields:
            Updated state after each agent completes
        """
        logger.info(f"Starting streaming workflow for query: {query[:100]}")
        
        # Create initial state
        state = create_initial_state(query, max_iterations)
        
        try:
            # Stream updates from graph
            for event in self.graph.stream(state):
                # Extract node name and updated values
                for node_name, node_state in event.items():
                    if node_name != "__end__":
                        logger.info(f"Agent completed: {node_name}")
                        
                        # Save checkpoint if enabled
                        if self.checkpointer:
                            self.checkpointer.save_checkpoint(
                                query, state["iteration"], node_name, node_state
                            )
                        
                        # Yield updated state
                        yield node_state
                
                # Update state for next iteration
                state.update(event)
            
            # Record end time
            state["end_time"] = time.time()
            state["elapsed_seconds"] = state["end_time"] - state["start_time"]
            
            logger.info(f"Workflow completed in {state['elapsed_seconds']:.2f}s")
            
        except Exception as e:
            logger.error(f"Streaming workflow failed: {str(e)}")
            raise
    
    def run_with_checkpoints(
        self,
        query: str,
        resume_from: Optional[str] = None,
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """Run workflow with checkpoint recovery capability.
        
        Args:
            query: User query to process
            resume_from: Optional checkpoint path to resume from
            max_iterations: Maximum revision cycles
        
        Returns:
            Final workflow state
        """
        logger.info(f"Starting workflow with checkpointing for query: {query[:100]}")
        
        # Load from checkpoint if provided
        if resume_from and self.checkpointer:
            state = self.checkpointer.load_checkpoint(resume_from)
            logger.info(f"Resumed from checkpoint: {resume_from}")
        else:
            state = create_initial_state(query, max_iterations)
        
        # Execute graph
        result = self.graph.invoke(state)
        
        # Record end time
        result["end_time"] = time.time()
        result["elapsed_seconds"] = result["end_time"] - result["start_time"]
        
        # Save final checkpoint
        if self.checkpointer:
            self.checkpointer.save_checkpoint(query, result["iteration"], "final", result)
        
        logger.info(f"Workflow completed with checkpointing")
        return result
    
    def get_execution_history(self, query: str) -> list:
        """Get list of checkpoints (execution history) for a query.
        
        Args:
            query: User query
        
        Returns:
            List of checkpoint paths in chronological order
        """
        if not self.checkpointer:
            return []
        
        return self.checkpointer.list_checkpoints(query)
    
    @staticmethod
    def _print_results(result: Dict[str, Any]) -> None:
        """Pretty print workflow results.
        
        Args:
            result: Final workflow state
        """
        print(f"\n{'='*80}")
        print("WORKFLOW COMPLETE")
        print(f"{'='*80}\n")
        
        print(f"Query: {result.get('query', 'N/A')}")
        print(f"Iterations: {result.get('iteration', 0)}")
        print(f"Execution Time: {result.get('elapsed_seconds', 0):.2f}s")
        
        print(f"\nAgent Completion Status:")
        print(f"  • Planner: {'✅' if result.get('planner_complete') else '❌'}")
        print(f"  • Researcher: {'✅' if result.get('researcher_complete') else '❌'}")
        print(f"  • Analyst: {'✅' if result.get('analyst_complete') else '❌'}")
        print(f"  • Writer: {'✅' if result.get('writer_complete') else '❌'}")
        print(f"  • Reviewer: {'✅' if result.get('reviewer_complete') else '❌'}")
        
        feedback = result.get('review_feedback', {})
        print(f"\nReview Result:")
        print(f"  • Quality Score: {feedback.get('quality_score', 0):.0%}")
        print(f"  • Recommendation: {feedback.get('recommendation', 'N/A')}")
        
        if result.get('final_answer'):
            print(f"\nFinal Answer Available: ✅ ({len(result['final_answer'])} chars)")
        else:
            print(f"\nFinal Answer: ❌ Not approved")
        
        print(f"\n{'='*80}\n")
