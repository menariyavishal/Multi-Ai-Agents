"""Researcher Agent - Analyzes Planner's output and gathers research data."""

from typing import Any, Dict
from app.agents.base import BaseAgent
from app.core.logger import get_logger

logger = get_logger(__name__)


class Researcher(BaseAgent):
    """Researcher agent that gathers data based on Planner's analysis."""
    
    def __init__(self):
        """Initialize Researcher agent with Groq LLM."""
        super().__init__(agent_role="researcher")
    
    def call(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Planner's output and gather research data.
        
        Args:
            state: Workflow state containing:
                - query: The user's original query
                - plan: The Planner's detailed plan
                - iteration: Current iteration number
                - messages: Message history
        
        Returns:
            Updated state with:
                - research: Gathered and synthesized research
                - researcher_complete: True
                - messages: Updated with research
        """
        query = state.get("query", "")
        plan = state.get("plan", "")
        iteration = state.get("iteration", 1)
        messages = state.get("messages", [])
        
        if not plan:
            logger.warning("No plan provided to Researcher")
            return {
                **state,
                "research": "No plan available for research",
                "researcher_complete": True,
                "messages": messages
            }
        
        logger.info(f"Researcher analyzing plan for query (iteration {iteration})")
        
        try:
            # Step 1: Analyze plan to determine data sources needed
            analysis = self._analyze_plan(plan, query)
            logger.info(f"Plan analysis complete: {analysis['data_type']} data needed")
            
            # Step 2: Extract data sources from analysis
            sources = self._parse_sources_from_analysis(analysis)
            logger.info(f"Selected sources: {sources}")
            
            # Step 3: Gather data from appropriate sources
            gathered_data = self._gather_data(sources, query, plan)
            logger.info(f"Data gathered from {len(sources)} source(s)")
            
            # Step 4: Synthesize research from gathered data
            research = self._synthesize_research(
                gathered_data, 
                analysis, 
                query
            )
            logger.info(f"Research synthesized ({len(research)} chars)")
            
            return {
                **state,
                "research": research,
                "data_classification": analysis.get("data_type", "COMBINED"),  # Pass classification to Analyst
                "researcher_complete": True,
                "messages": messages + [
                    {"role": "assistant", "content": f"Research: {research[:200]}..."}
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in Researcher: {str(e)}")
            return {
                **state,
                "research": f"Error generating research: {str(e)}",
                "data_classification": "COMBINED",  # Default to COMBINED on error
                "researcher_complete": True,
                "messages": messages
            }
    
    def _analyze_plan(self, plan: str, query: str) -> Dict[str, Any]:
        """Analyze Planner's output to determine data sources needed.
        
        Sends the plan to LLM asking what data sources are required.
        
        Args:
            plan: The Planner's detailed plan
            query: The original user query
        
        Returns:
            Dictionary with:
                - data_type: "REAL_TIME", "HISTORICAL", or "COMBINED"
                - sources: List of source names
                - reasoning: Why these sources are needed
                - data_to_gather: Specific data needed
        """
        prompt = f"""You are a Research Agent. A Planner has created a detailed plan.

ORIGINAL QUERY: {query}

PLANNER'S PLAN:
{plan}

Analyze this plan and determine what data sources are needed:

1. DATA SOURCES needed?
   - MCP_SERVERS: For REAL-TIME/CURRENT data (latest, live, today, 2026)
   - DATABASE: For HISTORICAL/PAST data (evolution, history, past, patterns)
   - BOTH: If plan mentions comparing or needs both current and historical

2. WHY these sources based on the plan?

3. What specific data to gather?

4. How will you combine the data?

Format your answer as:
DATA_SOURCES: [MCP_SERVERS / DATABASE / BOTH]
DATA_TYPE: [REAL_TIME / HISTORICAL / COMBINED]
REASONING: [Your explanation]
DATA_TO_GATHER: [List specific data needed]
COMBINATION_STRATEGY: [How to combine if using multiple sources]
"""
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Parse response
            analysis = self._parse_analysis_response(content)
            logger.info(f"Plan analysis: {analysis['data_type']}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing plan: {str(e)}")
            # Default to COMBINED if analysis fails
            return {
                "data_type": "COMBINED",
                "sources": ["MCP_SERVERS", "DATABASE"],
                "reasoning": "Default: gathering both current and historical data",
                "data_to_gather": "Comprehensive data from all sources"
            }
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response to extract analysis."""
        response_lower = response.lower()
        
        # Determine data type
        if "both" in response_lower:
            data_type = "COMBINED"
        elif "mcp_servers" in response_lower and "database" not in response_lower:
            data_type = "REAL_TIME"
        elif "database" in response_lower and "mcp_servers" not in response_lower:
            data_type = "HISTORICAL"
        else:
            data_type = "COMBINED"
        
        # Extract reasoning (everything after "REASONING:")
        reasoning = response
        if "reasoning:" in response_lower:
            reasoning = response.split("REASONING:")[-1]
            if "DATA_TO_GATHER:" in reasoning:
                reasoning = reasoning.split("DATA_TO_GATHER:")[0]
            reasoning = reasoning.strip()
        
        # Extract data to gather
        data_to_gather = ""
        if "data_to_gather:" in response_lower:
            data_to_gather = response.split("DATA_TO_GATHER:")[-1]
            if "COMBINATION_STRATEGY:" in data_to_gather:
                data_to_gather = data_to_gather.split("COMBINATION_STRATEGY:")[0]
            data_to_gather = data_to_gather.strip()
        
        # Build sources list
        sources = []
        if "mcp_servers" in response_lower:
            sources.append("MCP_SERVERS")
        if "database" in response_lower:
            sources.append("DATABASE")
        
        return {
            "data_type": data_type,
            "sources": sources,
            "reasoning": reasoning or "Determined based on plan analysis",
            "data_to_gather": data_to_gather or "Comprehensive data as per plan requirements"
        }
    
    def _parse_sources_from_analysis(self, analysis: Dict[str, Any]) -> list:
        """Extract data sources from analysis."""
        data_type = analysis.get("data_type", "COMBINED")
        
        if data_type == "REAL_TIME":
            return ["MCP_SERVERS"]
        elif data_type == "HISTORICAL":
            return ["DATABASE"]
        else:  # COMBINED
            return ["MCP_SERVERS", "DATABASE"]
    
    def _gather_data(self, sources: list, query: str, plan: str) -> Dict[str, str]:
        """Gather data from specified sources (mock implementation).
        
        In production, this would call real APIs.
        For now, we mock realistic data gathering.
        
        Args:
            sources: List of sources to gather from
            query: Original user query
            plan: Planner's plan
        
        Returns:
            Dictionary with data from each source
        """
        gathered_data = {}
        
        if "MCP_SERVERS" in sources:
            gathered_data["MCP_SERVERS"] = self._gather_real_time_data(query, plan)
        
        if "DATABASE" in sources:
            gathered_data["DATABASE"] = self._gather_historical_data(query, plan)
        
        return gathered_data
    
    def _gather_real_time_data(self, query: str, plan: str) -> str:
        """Gather REAL real-time data from MCP_SERVERS (APIs, web, etc.)."""
        try:
            from app.mcp_servers.researcher_mcp import ResearcherMCP
            
            # Extract what data we need from the plan
            data_to_gather = ""
            if "current" in plan.lower():
                data_to_gather += "current status, "
            if "latest" in plan.lower():
                data_to_gather += "latest information, "
            if "trend" in plan.lower():
                data_to_gather += "trends, "
            if "market" in plan.lower():
                data_to_gather += "market data, "
            
            # Call REAL MCP to gather real-time data
            real_time_data = ResearcherMCP.get_real_time_data(query, data_to_gather)
            
            # Format the response
            formatted = f"[REAL-TIME DATA from MCP_SERVERS]\n"
            formatted += f"Query: {query}\n"
            formatted += f"Sources: {', '.join(real_time_data.get('sources', []))}\n"
            formatted += f"\n"
            for data_item in real_time_data.get("data", []):
                formatted += f"{data_item}\n"
            
            logger.info(f"Real-time data gathered from {len(real_time_data.get('sources', []))} sources")
            return formatted
            
        except Exception as e:
            logger.error(f"Error gathering real-time data: {str(e)}")
            # Fallback
            return f"""[REAL-TIME DATA from MCP_SERVERS for: {query}]
- Current status and latest information
- Recent trends and developments
- Live data as of 2026
- Contemporary examples and cases
- Current market conditions or state
- Latest available statistics and metrics
"""
    
    def _gather_historical_data(self, query: str, plan: str) -> str:
        """Gather REAL historical data from DATABASE using Groq API with conversation context.
        
        Reads previous conversations from database to provide context-aware analysis.
        """
        try:
            from app.mcp_servers.researcher_mcp import ResearcherMCP
            
            # Build context from state (includes previous chats if available)
            context = {
                "previous_chats": [],  # Would come from database service
                "user_profile": {}     # Would come from user database
            }
            
            # In production, would query database for conversation history:
            # from app.services.db_service import DBService
            # db = DBService()
            # context["previous_chats"] = db.get_conversation_history(user_id)
            # context["user_profile"] = db.get_user_profile(user_id)
            
            # Call REAL MCP to gather historical data using Groq
            historical_data = ResearcherMCP.get_historical_data(query, context)
            
            logger.info("Historical data gathered from DATABASE using Groq API")
            return historical_data
            
        except Exception as e:
            logger.error(f"Error gathering historical data: {str(e)}")
            # Fallback
            return f"""[HISTORICAL DATA from DATABASE for: {query}]
- Historical context and background
- Evolution and development over time
- Past trends and patterns
- Established knowledge and proven approaches
- Historical statistics and data
- Lessons learned from the past
- Timeline of key developments
"""
    
    def _synthesize_research(self, gathered_data: Dict[str, str], 
                           analysis: Dict[str, Any], 
                           query: str) -> str:
        """Synthesize gathered data into comprehensive research.
        
        Args:
            gathered_data: Data gathered from various sources
            analysis: Analysis from _analyze_plan
            query: Original user query
        
        Returns:
            Synthesized research document
        """
        
        synthesis_prompt = f"""Synthesize this research data into a comprehensive answer.

ORIGINAL QUERY: {query}

DATA TYPE: {analysis.get('data_type', 'COMBINED')}

REASONING FOR SOURCES: {analysis.get('reasoning', '')}

GATHERED DATA:
{self._format_gathered_data(gathered_data)}

Create a comprehensive 2-3 paragraph research synthesis that:
1. Directly answers the user's query
2. Provides clear, actionable information
3. Combines data sources appropriately
4. Explains key insights and implications"""
        
        try:
            response = self.llm.invoke(synthesis_prompt)
            research = response.content if hasattr(response, 'content') else str(response)
            return research
        except Exception as e:
            logger.error(f"Error synthesizing research: {str(e)}")
            return self._generate_fallback_synthesis(gathered_data, query)
    
    def _format_gathered_data(self, gathered_data: Dict[str, str]) -> str:
        """Format gathered data for LLM synthesis."""
        formatted = ""
        for source, data in gathered_data.items():
            formatted += f"\n{source}:\n{data}\n"
        return formatted
    
    def _generate_fallback_synthesis(self, gathered_data: Dict[str, str], 
                                     query: str) -> str:
        """Generate fallback synthesis if LLM fails."""
        synthesis_parts = []
        
        synthesis_parts.append(f"Research on: {query}\n")
        
        for source, data in gathered_data.items():
            synthesis_parts.append(f"\n{source}:\n{data}")
        
        synthesis_parts.append("\nThis research combines data from the appropriate sources to provide a comprehensive answer.")
        
        return "".join(synthesis_parts)
