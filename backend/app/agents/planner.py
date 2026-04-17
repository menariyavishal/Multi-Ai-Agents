"""Planner Agent - Creates comprehensive plans for queries using Groq LLM."""

from typing import Any, Dict
from app.agents.base import BaseAgent
from app.core.logger import get_logger

logger = get_logger(__name__)


class Planner(BaseAgent):
    """Planner agent that creates comprehensive plans for given tasks."""
    
    def __init__(self):
        """Initialize Planner agent with Groq LLM."""
        super().__init__(agent_role="planner")
    
    def call(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive plan for the query.
        
        Args:
            state: Workflow state containing:
                - query: The user's query/task
                - iteration: Current iteration number
                - (optional) context: Additional context
        
        Returns:
            Updated state with:
                - plan: Generated comprehensive plan
                - planner_complete: True
        """
        query = state.get("query", "")
        iteration = state.get("iteration", 1)
        context = state.get("context", "")
        
        if not query:
            logger.warning("No query provided to Planner")
            return {
                **state,
                "plan": "No query provided",
                "planner_complete": True
            }
        
        # Build the prompt for planning
        prompt = self._build_planning_prompt(query, context, iteration)
        
        logger.info(f"Planner generating plan for query (iteration {iteration})")
        
        try:
            # Invoke Groq LLM for planning
            response = self.llm.invoke(prompt)
            plan = response.content if hasattr(response, 'content') else str(response)
            
            logger.info(f"Planner successfully generated plan ({len(plan)} chars)")
            
            return {
                **state,
                "plan": plan,
                "planner_complete": True,
                "messages": state.get("messages", []) + [
                    {"role": "assistant", "content": f"Plan: {plan[:200]}..."}
                ]
            }
        
        except Exception as e:
            logger.error(f"Planner failed: {e}")
            return {
                **state,
                "plan": f"Error generating plan: {str(e)}",
                "planner_complete": True,
                "error": str(e)
            }
    
    def _build_planning_prompt(self, query: str, context: str, iteration: int) -> str:
        """Build a comprehensive planning prompt.
        
        Args:
            query: User's query/task
            context: Optional additional context
            iteration: Current iteration number
        
        Returns:
            Formatted prompt for Groq LLM
        """
        prompt = f"""You are an expert planning agent. Your task is to create a comprehensive and detailed plan.

TASK: {query}

{"ADDITIONAL CONTEXT: " + context if context else ""}

ITERATION: {iteration}

Please generate a detailed, structured plan that includes:
1. **Objectives** - Clear goals for this task
2. **Key Steps** - Main phases/components needed
3. **Resources** - What resources/skills are required
4. **Timeline** - Approximate timeline for each phase
5. **Potential Risks** - Challenges to consider
6. **Success Metrics** - How to measure success

Provide a thorough, actionable plan that can guide execution."""
        
        return prompt
