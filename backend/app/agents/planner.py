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
            
            # Extract data type needed from Planner's analysis
            data_type_needed = self._extract_data_type_needed(plan)
            logger.info(f"Planner determined data type needed: {data_type_needed}")
            
            logger.info(f"Planner successfully generated plan ({len(plan)} chars)")
            
            return {
                **state,
                "plan": plan,
                "data_type_needed": data_type_needed,  # Pass Planner's intelligence to Researcher
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
                "data_type_needed": "COMBINED",  # Default to COMBINED on error
                "planner_complete": True,
                "error": str(e)
            }
    
    def _extract_data_type_needed(self, plan: str) -> str:
        """Extract DATA_TYPE_NEEDED from Planner's plan analysis.
        
        Args:
            plan: The full plan output from LLM
        
        Returns:
            "REAL_TIME", "HISTORICAL", or "COMBINED"
        """
        plan_lower = plan.lower()
        
        # Look for explicit DATA_TYPE_NEEDED in response
        if "data_type_needed:" in plan_lower:
            lines = plan.split("\n")
            for line in lines:
                if "data_type_needed:" in line.lower():
                    # Extract the value after the colon
                    data_type = line.split(":")[-1].strip().upper()
                    if data_type in ["REAL_TIME", "HISTORICAL", "COMBINED"]:
                        return data_type
        
        # Fallback: default to COMBINED if extraction fails
        logger.warning("Could not extract DATA_TYPE_NEEDED from Planner output, defaulting to COMBINED")
        return "COMBINED"
    
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

**CRITICAL: Data Requirements Analysis**
Before finalizing the plan, analyze what data is required:

Determine DATA_TYPE_NEEDED based on the task nature:
- REAL_TIME: If plan requires current/live/latest information from APIs or web
- HISTORICAL: If plan requires past data, history, patterns, evolution, stored data
- COMBINED: If plan requires BOTH current and historical data for comparison or context

Reasoning: Analyze the task deeply. Does it need:
- Today's weather? -> REAL_TIME
- History of stock prices over 5 years? -> HISTORICAL  
- Comparing today's market vs historical trends? -> COMBINED
- Latest news today? -> REAL_TIME
- How AI evolved? -> HISTORICAL
- Current AI trends vs historical development? -> COMBINED

At the END of your response, add:
DATA_TYPE_NEEDED: [REAL_TIME/HISTORICAL/COMBINED]
DATA_REASONING: [Brief explanation of why this data type]

Provide a thorough, actionable plan that can guide execution."""
        
        return prompt
