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
                - user_id: User identifier for database context
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
        user_id = state.get("user_id", "")
        iteration = state.get("iteration", 1)
        messages = state.get("messages", [])
        
        # Store user_id for use in data gathering methods
        self._current_user_id = user_id
        
        if not plan:
            logger.warning("No plan provided to Researcher")
            return {
                **state,
                "research": "No plan available for research",
                "researcher_complete": True,
                "messages": messages
            }
        
        logger.info(f"Researcher analyzing plan for user {user_id} (iteration {iteration})")
        
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
        """Gather REAL historical data from DATABASE + Groq LLM's own knowledge.
        
        Combines:
        1. Previous conversations from MongoDB (user's personal history)
        2. Groq LLM's own knowledge (general historical knowledge and patterns)
        
        Returns: Enhanced historical analysis with both sources combined.
        """
        try:
            from app.services.database_service import get_db_service
            
            # Get user_id from current context (if available)
            user_id = getattr(self, '_current_user_id', None)
            
            # Build context from previous chats
            database_context = {
                "previous_chats": [],
                "user_profile": {}
            }
            
            # Query MongoDB for user's conversation history
            if user_id:
                try:
                    db_service = get_db_service()
                    
                    if db_service.is_connected():
                        # Get user's last 5 conversations for context
                        previous_convs = db_service.get_user_conversations(user_id, limit=5, skip=0)
                        
                        # Format previous conversations for context
                        database_context["previous_chats"] = [
                            {
                                "query": conv.query,
                                "summary": conv.title,
                                "created_at": str(conv.created_at),
                                "quality_score": conv.quality_score
                            }
                            for conv in previous_convs
                        ]
                        
                        # Get user profile for additional context
                        user_profile = db_service.get_user(user_id)
                        if user_profile:
                            database_context["user_profile"] = {
                                "total_conversations": user_profile.total_conversations,
                                "average_quality_score": user_profile.average_quality_score,
                                "email": user_profile.email,
                                "name": user_profile.name
                            }
                        
                        logger.info(f"Retrieved {len(database_context['previous_chats'])} previous chats for user {user_id}")
                    else:
                        logger.warning("MongoDB not connected - will use Groq's knowledge only")
                        
                except Exception as db_error:
                    logger.warning(f"Error fetching conversation history: {str(db_error)}")
                    # Continue without database context - Groq can still help
            
            # Now send database context + query to Groq LLM to combine with its own knowledge
            historical_data = self._synthesize_with_groq_knowledge(query, plan, database_context)
            
            logger.info("Historical data synthesized from DATABASE context + Groq LLM knowledge")
            return historical_data
            
        except Exception as e:
            logger.error(f"Error gathering historical data: {str(e)}")
            # Fallback - just use Groq's knowledge
            return f"""[HISTORICAL DATA from Groq LLM for: {query}]
- Historical context and background
- Evolution and development over time
- Past trends and patterns
- Established knowledge and proven approaches
- Historical statistics and data
- Lessons learned from the past
- Timeline of key developments
"""
    
    def _synthesize_with_groq_knowledge(self, query: str, plan: str, database_context: Dict) -> str:
        """Use Groq LLM to combine database context with its own knowledge.
        
        Sends both sources to Groq and asks it to synthesize them.
        This is the "brain" of the researcher - it thinks and reasons.
        
        Args:
            query: Original user query
            plan: Planner's plan for what to research
            database_context: User's previous conversations from MongoDB
        
        Returns:
            Synthesized historical analysis combining both sources
        """
        
        # Format database context for LLM
        db_context_str = self._format_database_context(database_context)
        
        # Build prompt asking Groq to use BOTH sources
        prompt = f"""You are a Historical Research Expert. Combine TWO sources to provide comprehensive historical knowledge.

USER QUERY: {query}

PLANNER'S RESEARCH PLAN: {plan}

SOURCE 1 - DATABASE (User's Previous Conversations):
{db_context_str}

SOURCE 2 - YOUR OWN KNOWLEDGE (Groq LLM):
Use your training data to provide:
- Historical context and background
- Evolution and development patterns over time
- Past trends that are relevant
- Established proven approaches
- Historical statistics and data
- Timeline of key developments
- Lessons learned from history that apply here

TASK: Synthesize both sources to provide:
1. **Database Insights**: What we learned from user's previous conversations
2. **Historical Knowledge**: What history and past patterns tell us
3. **Combined Analysis**: How these sources together inform the current query
4. **Recommendations**: Lessons from the past that apply to this situation

Format your answer as a comprehensive historical research report that combines:
- Specific examples from user's database (if available)
- General historical knowledge and patterns
- How history informs current understanding"""
        
        try:
            response = self.llm.invoke(prompt)
            historical_knowledge = response.content if hasattr(response, 'content') else str(response)
            
            logger.info(f"Groq synthesized {len(historical_knowledge)} chars of historical knowledge combining database + own knowledge")
            
            return f"[HISTORICAL DATA: Database Context + Groq LLM Knowledge]\n\n{historical_knowledge}"
            
        except Exception as e:
            logger.error(f"Error synthesizing with Groq: {str(e)}")
            # Fallback to just database context
            return f"[HISTORICAL DATA from Database]\n{db_context_str}"
    
    def _format_database_context(self, database_context: Dict) -> str:
        """Format database context for LLM readability."""
        formatted = ""
        
        # Add user profile if available
        if database_context.get("user_profile"):
            profile = database_context["user_profile"]
            formatted += f"USER PROFILE:\n"
            formatted += f"- Name: {profile.get('name', 'N/A')}\n"
            formatted += f"- Total Conversations: {profile.get('total_conversations', 0)}\n"
            formatted += f"- Average Quality Score: {profile.get('average_quality_score', 'N/A')}\n\n"
        
        # Add previous conversations
        if database_context.get("previous_chats"):
            formatted += f"PREVIOUS CONVERSATIONS (Last 5):\n"
            for i, chat in enumerate(database_context["previous_chats"], 1):
                formatted += f"\n{i}. Query: {chat.get('query', 'N/A')}\n"
                formatted += f"   Summary: {chat.get('summary', 'N/A')}\n"
                formatted += f"   Quality: {chat.get('quality_score', 'N/A')}\n"
                formatted += f"   Date: {chat.get('created_at', 'N/A')}\n"
        else:
            formatted += "NO PREVIOUS CONVERSATIONS - First time this user is asking about this topic\n"
        
        return formatted
    
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
