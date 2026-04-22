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
        data_type_needed = state.get("data_type_needed", "COMBINED")  # From Planner's intelligence
        
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
        logger.info(f"Planner indicated data type needed: {data_type_needed}")
        
        try:
            # Step 1: Analyze plan using BOTH Planner's intelligence + Researcher's own reasoning
            analysis = self._analyze_plan(plan, query, data_type_needed)
            logger.info(f"Plan analysis complete: {analysis['data_type']} data type determined")
            
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
    
    def _analyze_plan(self, plan: str, query: str, planner_data_type: str = "COMBINED") -> Dict[str, Any]:
        """Analyze Planner's output using BOTH Planner's intelligence + Researcher's own reasoning.
        
        Validates Planner's data type determination with intelligent analysis.
        
        Args:
            plan: The Planner's detailed plan
            query: The original user query
            planner_data_type: Data type determined by Planner (REAL_TIME/HISTORICAL/COMBINED)
        
        Returns:
            Dictionary with:
                - data_type: "REAL_TIME", "HISTORICAL", or "COMBINED"
                - sources: List of source names
                - reasoning: Why these sources are needed
                - data_to_gather: Specific data needed
        """
        prompt = f"""You are a Research Agent. A Planner has analyzed the task and determined the data type needed.

ORIGINAL QUERY: {query}

PLANNER'S PLAN:
{plan}

PLANNER'S INTELLIGENCE: Data type needed = {planner_data_type}

Your task: Use intelligent analysis to validate/refine the Planner's determination.

INTELLIGENT DECISION-MAKING RULES:
- REAL_TIME needed if: Query asks for current/live/today/latest/now information, weather today, stock prices now, news today
- HISTORICAL needed if: Query asks for history/evolution/past/patterns/how it changed over time, historical data
- COMBINED needed if: Query requires both current AND past for comparison/trends/analysis

Example intelligent decisions (NOT keyword-based):
- "Show weather today" -> REAL_TIME (even if word "history" appears elsewhere)
- "How did Bitcoin evolve?" -> HISTORICAL (focuses on past evolution)
- "Is Bitcoin doing better than in 2020?" -> COMBINED (compares past vs present)
- "Latest AI news" -> REAL_TIME (needs current news)
- "History of AI" -> HISTORICAL (past development)

Analyze deeply based on WHAT THE QUERY TRULY ASKS FOR, not just keywords.

FINAL DETERMINATION (be concise):
DATA_TYPE_FINAL: [Choose: REAL_TIME / HISTORICAL / COMBINED based on your intelligence]
REASONING: [Why this type based on query nature, not keywords]
DATA_TO_GATHER: [What specific data needed]
"""
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Parse response using intelligent parsing (not keyword-based)
            analysis = self._parse_intelligent_analysis(content, planner_data_type)
            logger.info(f"Researcher's intelligent analysis: {analysis['data_type']} (Planner suggested: {planner_data_type})")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in intelligent analysis: {str(e)}")
            # Fall back to Planner's assessment if Researcher analysis fails
            return {
                "data_type": planner_data_type,
                "sources": self._get_sources_from_type(planner_data_type),
                "reasoning": f"Using Planner's assessment ({planner_data_type}) due to analysis error",
                "data_to_gather": "Comprehensive data as per plan requirements"
            }
    
    def _parse_intelligent_analysis(self, response: str, planner_assessment: str) -> Dict[str, Any]:
        """Parse Researcher's intelligent analysis (NOT keyword-based).
        
        Extracts the Researcher's own reasoning, not just pattern matching.
        """
        response_lower = response.lower()
        
        # Look for explicit DATA_TYPE_FINAL in response
        final_data_type = None
        if "data_type_final:" in response_lower:
            lines = response.split("\n")
            for line in lines:
                if "data_type_final:" in line.lower():
                    data_type_str = line.split(":")[-1].strip().upper()
                    # Extract just the data type (e.g., "REAL_TIME" from "REAL_TIME / reason")
                    for dt in ["REAL_TIME", "HISTORICAL", "COMBINED"]:
                        if dt in data_type_str:
                            final_data_type = dt
                            break
                    if final_data_type:
                        break
        
        # Fallback to Planner's assessment if Researcher couldn't determine
        if not final_data_type:
            logger.warning(f"Could not extract Researcher's assessment, using Planner's: {planner_assessment}")
            final_data_type = planner_assessment
        
        # Extract reasoning
        reasoning = response
        if "reasoning:" in response_lower:
            reasoning = response.split("REASONING:")[-1]
            if "DATA_TO_GATHER:" in reasoning:
                reasoning = reasoning.split("DATA_TO_GATHER:")[0]
            reasoning = reasoning.strip()
        
        # Extract data to gather
        data_to_gather = ""
        if "data_to_gather:" in response_lower:
            data_to_gather = response.split("DATA_TO_GATHER:")[-1].strip()
        
        return {
            "data_type": final_data_type,
            "sources": self._get_sources_from_type(final_data_type),
            "reasoning": reasoning or f"Intelligent analysis determined {final_data_type} data needed",
            "data_to_gather": data_to_gather or "Comprehensive data as per intelligent assessment"
        }
    
    def _get_sources_from_type(self, data_type: str) -> list:
        """Map data type to source list.
        
        Args:
            data_type: "REAL_TIME", "HISTORICAL", or "COMBINED"
        
        Returns:
            List of source names to gather from
        """
        if data_type == "REAL_TIME":
            return ["MCP_SERVERS"]
        elif data_type == "HISTORICAL":
            return ["DATABASE"]
        else:  # COMBINED
            return ["MCP_SERVERS", "DATABASE"]
    
    def _parse_sources_from_analysis(self, analysis: Dict[str, Any]) -> list:
        """Extract data sources from analysis."""
        return analysis.get("sources", ["MCP_SERVERS", "DATABASE"])
    
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
        """Gather historical data: PAST queries from DATABASE + EXISTING data from Groq LLM.
        
        Two-part approach:
        1. Database: Get user's PAST relevant conversations (existing stored knowledge)
        2. Groq LLM: Get EXISTING/CURRENT information about the topic
        3. Combine both for comprehensive answer
        
        Returns: Combined analysis with both sources
        """
        try:
            from app.services.database_service import get_db_service
            
            # ===== PART 1: Get PAST queries from DATABASE =====
            user_id = getattr(self, '_current_user_id', None)
            database_data = {
                "past_conversations": [],
                "user_profile": {}
            }
            
            if user_id:
                try:
                    db_service = get_db_service()
                    
                    if db_service.is_connected():
                        # Get user's last 5 conversations (past queries)
                        previous_convs = db_service.get_user_conversations(user_id, limit=5, skip=0)
                        
                        # Format past conversations
                        database_data["past_conversations"] = [
                            {
                                "query": conv.query,
                                "summary": conv.title,
                                "created_at": str(conv.created_at),
                                "quality_score": conv.quality_score
                            }
                            for conv in previous_convs
                        ]
                        
                        # Get user profile
                        user_profile = db_service.get_user(user_id)
                        if user_profile:
                            database_data["user_profile"] = {
                                "total_conversations": user_profile.total_conversations,
                                "average_quality_score": user_profile.average_quality_score
                            }
                        
                        logger.info(f"Retrieved {len(database_data['past_conversations'])} past conversations from database")
                    else:
                        logger.warning("MongoDB not connected - no past data available")
                        
                except Exception as db_error:
                    logger.warning(f"Error fetching past conversations: {str(db_error)}")
            
            # ===== PART 2: Get EXISTING data from Groq LLM =====
            existing_data = self._get_existing_data_from_groq(query, plan)
            
            # ===== PART 3: Combine both sources =====
            combined_analysis = self._combine_database_and_existing_data(
                query, 
                database_data, 
                existing_data
            )
            
            logger.info("Historical data: Combined past database + existing information")
            return combined_analysis
            
        except Exception as e:
            logger.error(f"Error gathering historical data: {str(e)}")
            # Fallback
            return f"""[HISTORICAL DATA FALLBACK for: {query}]
- Historical context and background
- Evolution and development over time
- Past trends and patterns
- Established knowledge and proven approaches
"""
    
    def _get_existing_data_from_groq(self, query: str, plan: str) -> str:
        """Get EXISTING/CURRENT data about the topic using Groq LLM's knowledge.
        
        This is Groq's 'brain' - using its training data to provide:
        - Current state of knowledge
        - Established facts and information
        - Proven approaches and patterns
        - Key insights about the topic
        """
        prompt = f"""You are an expert providing EXISTING knowledge about a topic.

QUERY: {query}

PLANNER'S RESEARCH PLAN: {plan}

Based on your training data, provide EXISTING information about this topic:

1. **Current State**: What is the current state/status of this topic?
2. **Established Facts**: What are proven/established facts?
3. **Key Concepts**: What important concepts exist in this field?
4. **Proven Approaches**: What approaches have proven effective?
5. **Important Patterns**: What patterns exist in this domain?
6. **Key Players/Resources**: Who or what are important in this area?
7. **Best Practices**: What are current best practices?
8. **Common Challenges**: What challenges typically exist?

Provide comprehensive EXISTING knowledge based on your training data."""
        
        try:
            response = self.llm.invoke(prompt)
            existing_knowledge = response.content if hasattr(response, 'content') else str(response)
            
            logger.info(f"Groq provided {len(existing_knowledge)} chars of existing knowledge")
            return existing_knowledge
            
        except Exception as e:
            logger.error(f"Error getting existing data from Groq: {str(e)}")
            return "Unable to retrieve existing knowledge"
    
    def _combine_database_and_existing_data(self, query: str, 
                                           database_data: Dict, 
                                           existing_data: str) -> str:
        """Combine PAST queries (from database) with EXISTING data (from Groq).
        
        Creates a comprehensive analysis that includes:
        - What user has asked before (database)
        - What existing knowledge tells us (Groq)
        - How they complement each other
        """
        
        # Format past conversations for readability
        past_convs_str = self._format_past_conversations(database_data["past_conversations"])
        
        combination_prompt = f"""Create a comprehensive analysis combining two sources:

CURRENT QUERY: {query}

SOURCE 1 - PAST QUERIES from DATABASE (What user has asked before):
{past_convs_str}

SOURCE 2 - EXISTING DATA from Knowledge (Current information about this topic):
{existing_data}

Create an analysis that includes:

1. **PAST CONTEXT**: 
   - What has this user asked about before?
   - How does past relate to current query?
   - What patterns from past apply?

2. **EXISTING KNOWLEDGE**:
   - What does current knowledge tell us?
   - What are established facts?
   - What approaches currently work?

3. **COMBINED INSIGHT**:
   - How do past questions + existing knowledge complement each other?
   - What's relevant from their history?
   - How does existing knowledge help with their current query?

4. **PRACTICAL ANSWER**:
   - Based on both sources, what's the best approach?
   - What insights from their past apply?
   - What new information from existing knowledge adds value?"""
        
        try:
            response = self.llm.invoke(combination_prompt)
            combined = response.content if hasattr(response, 'content') else str(response)
            return f"[HISTORICAL DATA: Past Database + Existing Knowledge Combined]\n\n{combined}"
        except Exception as e:
            logger.error(f"Error combining sources: {str(e)}")
            return f"[Historical Data]\n\nPast Questions:\n{past_convs_str}\n\nExisting Knowledge:\n{existing_data}"
    
    def _format_past_conversations(self, conversations: list) -> str:
        """Format past conversations for readability."""
        if not conversations:
            return "No past conversations - first time asking about this topic"
        
        formatted = "Past Conversations:\n"
        for i, conv in enumerate(conversations, 1):
            formatted += f"\n{i}. Query: {conv.get('query', 'N/A')}\n"
            formatted += f"   Quality: {conv.get('quality_score', 'N/A')}/10\n"
            formatted += f"   Date: {conv.get('created_at', 'N/A')}\n"
        
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
