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
        """Gather REAL real-time data from MCP_SERVERS (APIs, web, etc.).
        
        FALLBACK MECHANISM:
        1. First tries to get data from real APIs/MCPs
        2. If APIs fail or return empty data → Falls back to Groq LLM knowledge
        """
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
            
            # CHECK: Did we actually get any data?
            sources = real_time_data.get('sources', [])
            data_items = real_time_data.get('data', [])
            
            logger.info(f"MCP returned: {len(sources)} sources, {len(data_items)} data items")
            for i, source in enumerate(sources):
                logger.info(f"  Source {i}: {source}")
                if i < len(data_items):
                    logger.info(f"  Data {i} length: {len(str(data_items[i]))}")
            
            # If NO data was gathered from APIs, trigger fallback to Groq
            if not sources or len(sources) == 0 or not data_items or len(data_items) == 0:
                logger.warning(f"No data from real-time APIs (sources: {len(sources)}, data: {len(data_items)}). Falling back to Groq LLM.")
                return self._fallback_to_groq_knowledge(query, plan)
            
            # Format the response with actual data  
            formatted = f"[REAL-TIME DATA from MCP_SERVERS]\n"
            formatted += f"Query: {query}\n"
            formatted += f"Sources: {', '.join(sources)}\n"
            formatted += f"\n"
            for i, data_item in enumerate(data_items):
                formatted += f"Data Item {i+1}:\n{data_item}\n\n"
            
            logger.info(f"Real-time data gathered from {len(sources)} sources, formatted length: {len(formatted)}")
            return formatted
            
        except Exception as e:
            logger.error(f"Error gathering real-time data from APIs: {str(e)}")
            logger.info(f"Falling back to Groq LLM knowledge for: {query}")
            
            # FALLBACK: Use Groq LLM to provide knowledge about the topic
            return self._fallback_to_groq_knowledge(query, plan)
    
    def _clean_thinking_blocks(self, text: str) -> str:
        """Remove thinking blocks and incomplete tags from text - AGGRESSIVE cleaning.
        
        Args:
            text: Text that may contain thinking blocks
        
        Returns:
            Cleaned text without thinking blocks
        """
        if not text:
            return text
        
        import re as re_module
        
        # AGGRESSIVE Step 1: Remove lines/sections that contain think markers (even incomplete)
        # This handles: **<think> ... , <think>..., **text<think>
        lines = []
        skip_mode = False  # Track if we're in a thinking block
        
        for line in text.split('\n'):
            # Check if line contains thinking start marker
            if '<think>' in line or '**<think>' in line:
                skip_mode = True
                # Skip this line entirely
                continue
            
            # Check if line contains thinking end marker  
            if '</think>' in line or ('**' in line and skip_mode):
                skip_mode = False
                # Skip this line too
                continue
                
            # If we're in skip mode, skip this line
            if skip_mode:
                continue
            
            # Skip obvious thinking fragments (lines that look like incomplete thoughts)
            line_stripped = line.strip()
            if not line_stripped:
                lines.append(line)
                continue
            
            # Skip lines that are too short AND start with thinking markers
            if len(line_stripped) < 20 and any(marker in line_stripped for marker in 
                ['Okay,', 'Let me', 'Wait,', 'Actually,', 'I think', 'Hmm,', 'I need',
                 'Let me start', 'I know', 'But', 'Hmm', 'But wait']):
                continue
            
            lines.append(line)
        
        text = '\n'.join(lines)
        
        # AGGRESSIVE Step 2: Use regex to strip ANY remaining thinking markers
        # Match complete think blocks: **<think>...content...</think>
        text = re_module.sub(r'\*\*<think>.*?</think>', '', text, flags=re_module.DOTALL)
        # Match incomplete think blocks ending with **: **<think>...content**
        text = re_module.sub(r'\*\*<think>[^*]*(?:\*(?!\*))*\*\*', '', text, flags=re_module.DOTALL)
        # Match <think>...</think>
        text = re_module.sub(r'<think>.*?</think>', '', text, flags=re_module.DOTALL)
        # Match incomplete <think>...[anything]
        text = re_module.sub(r'<think>[^<]*(?:</think>)?', '', text, flags=re_module.DOTALL)
        # Remove any remaining **<think> or <think> markers
        text = re_module.sub(r'\*\*?<think>', '', text)
        # Remove orphaned ** that marks truncation
        text = re_module.sub(r'\s\*\*\s*$', '', text, flags=re_module.MULTILINE)
        text = re_module.sub(r'\*\*$', '', text, flags=re_module.MULTILINE)
        
        # AGGRESSIVE Step 3: Remove truncated lines
        lines = text.split('\n')
        final_lines = []
        for line in lines:
            # Skip lines that look truncated/incomplete
            if line.rstrip().endswith(('the re', 'the user', 'asking', 'know', 'But', 'Hmm')):
                continue
            # Skip lines that end with fragment + ** which indicates truncation
            if '**' in line and len(line.rstrip()) < 50:
                continue
            final_lines.append(line)
        
        text = '\n'.join(final_lines)
        
        return text.strip()
    
    def _fallback_to_groq_knowledge(self, query: str, plan: str) -> str:
        """FALLBACK: When real-time APIs are unavailable or fail, use Groq LLM knowledge.
        
        Groq provides comprehensive knowledge based on training data.
        This ensures users get answers even if APIs are down.
        
        Intelligently tailors the prompt based on query type to extract ACTUAL values.
        """
        # Detect query type and customize prompt accordingly
        query_lower = query.lower()
        
        # Weather/Temperature queries
        weather_keywords = ['temperature', 'weather', 'temp', 'celsius', 'fahrenheit', 'climate', 'hot', 'cold', 'degree']
        is_weather_query = any(keyword in query_lower for keyword in weather_keywords)
        
        # Stock/Financial queries
        stock_keywords = ['stock', 'price', 'share', 'market', 'gdp', 'inflation', 'rate', 'yield', 'valuation']
        is_stock_query = any(keyword in query_lower for keyword in stock_keywords)
        
        # Crypto queries
        crypto_keywords = ['bitcoin', 'ethereum', 'crypto', 'blockchain', 'btc', 'eth', 'coin', 'cryptocurrency']
        is_crypto_query = any(keyword in query_lower for keyword in crypto_keywords)
        
        # News/Current events queries
        news_keywords = ['news', 'latest', 'current', 'today', 'happening', 'recent', 'breaking', 'event']
        is_news_query = any(keyword in query_lower for keyword in news_keywords)
        
        # Sports queries
        sports_keywords = ['score', 'match', 'game', 'sport', 'player', 'team', 'league', 'champion']
        is_sports_query = any(keyword in query_lower for keyword in sports_keywords)
        
        # Build specialized prompt based on query type
        if is_weather_query:
            prompt = f"""Answer this question about weather/temperature in Panvel:

QUERY: {query}

Provide SPECIFIC TEMPERATURE VALUES with numbers. Use your knowledge of this location's climate to provide reasonable estimates if real-time data isn't available:

1. **Temperature Range**: What temperatures would be typical or expected for this location in this time period? (Include specific Celsius or Fahrenheit numbers)
2. **Weather Pattern**: What weather pattern is typical for this time of year?
3. **Seasonal Info**: What's the general climate like during this season?
4. **Specific Details**: Humidity, wind patterns if known

IMPORTANT: Provide SPECIFIC NUMBERS (e.g., "25-30°C" not "warm"). Give concrete temperature values.
Format: Location [City/Area], Temperature [specific range or value with unit], Conditions [weather type]"""
        
        elif is_stock_query:
            prompt = f"""Answer this question about stocks/financial data:

QUERY: {query}

Provide SPECIFIC FINANCIAL NUMBERS and values. Use your training data knowledge to provide the best available information:

1. **Price/Value**: What are the SPECIFIC numbers? (e.g., "$185.50" not "high"). Include currency.
2. **Change**: What's the change percentage or direction? (e.g., "+2.5%" or "+$3.50")
3. **Key Metrics**: P/E ratio, market cap, or other relevant numbers if you know them
4. **Context**: Why might this value matter?

IMPORTANT: ALWAYS provide SPECIFIC NUMBERS - give a range or typical value if exact isn't known (e.g., "typically ranges from $150-$200").
Format: Company/Asset, Price [specific number with currency], Change [specific number/percentage]"""
        
        elif is_crypto_query:
            prompt = f"""Answer this question about cryptocurrency prices:

QUERY: {query}

Provide SPECIFIC CRYPTO PRICES. Use your training data knowledge to give concrete numbers:

1. **Current Price**: What's the SPECIFIC price? (e.g., "$45,200" not "expensive"). Must include USD amount.
2. **Price Change**: What's the recent change? (e.g., "+3.2%" or "-$1,500")
3. **Market Data**: Market cap or 24h trading volume if known
4. **Trend**: Is price going up, down, or sideways?

IMPORTANT: ALWAYS provide SPECIFIC NUMBERS - if you don't know exact current price, give a reasonable estimate based on your training data (e.g., "typically ranges $40,000-$50,000 USD").
Format: Cryptocurrency Name, Price [$specific USD amount], Change [specific amount/percentage]"""
        
        elif is_news_query:
            prompt = f"""IMPORTANT: User is asking for CURRENT NEWS and LATEST INFORMATION.

QUERY: {query}

Provide the CURRENT and LATEST information based on your training data:

1. **Latest Events**: What are the most recent events or breaking news?
2. **Current Situation**: What is happening right now?
3. **Key Details**: Who, what, when, where, why - specific facts
4. **Impact & Significance**: Why is this important?
5. **Time Context**: When did this happen? How recent?

IMPORTANT: Provide SPECIFIC, CURRENT information.
Focus on the LATEST and MOST RECENT developments."""
        
        elif is_sports_query:
            prompt = f"""IMPORTANT: User is asking for CURRENT SPORTS INFORMATION.

QUERY: {query}

Provide the CURRENT sports data based on your training data:

1. **Current Scores**: What are the current/recent scores? (Include specific numbers)
2. **Game Status**: What's the status? (ongoing, completed, scheduled)
3. **Team/Player Stats**: Relevant statistics and performance data
4. **Recent Results**: Latest matches or performances
5. **Data Source & Time**: When this information is from

IMPORTANT: Provide SPECIFIC SCORES and actual numbers.
Be precise about current game/match situations."""
        
        else:
            # Generic real-time query
            prompt = f"""IMPORTANT: User is asking for CURRENT/REAL-TIME INFORMATION.

QUERY: {query}

Provide CURRENT and REAL-TIME data based on your training data:

1. **Current Values**: What are the current/recent actual measurements, statistics, or values? (Include specific numbers)
2. **Key Data**: What specific data points are relevant?
3. **Status/Condition**: What is the current status or state?
4. **Trend**: Is it changing? How?
5. **Time Context**: When is this data from?

IMPORTANT: Provide SPECIFIC NUMBERS and actual values - not generic descriptions.
Focus on CURRENT/REAL-TIME data with precision."""
        
        try:
            response = self.llm.invoke(prompt)
            groq_knowledge = response.content if hasattr(response, 'content') else str(response)
            
            # AGGRESSIVE clean up of thinking blocks
            groq_knowledge = self._clean_thinking_blocks(groq_knowledge)
            
            # Determine data source label
            if is_weather_query:
                source_label = "(Real-time Weather APIs unavailable - using trained knowledge as of training date)"
            elif is_stock_query:
                source_label = "(Real-time Financial APIs unavailable - using trained knowledge)"
            elif is_crypto_query:
                source_label = "(Real-time Crypto APIs unavailable - using trained knowledge)"
            elif is_news_query:
                source_label = "(Real-time News APIs unavailable - using trained knowledge)"
            elif is_sports_query:
                source_label = "(Real-time Sports APIs unavailable - using trained knowledge)"
            else:
                source_label = "(Real-time APIs unavailable - using trained knowledge)"
            
            formatted = f"[DATA from Groq LLM Knowledge]\n"
            formatted += f"{source_label}\n\n"
            formatted += f"Query: {query}\n\n"
            formatted += groq_knowledge
            
            logger.info(f"Fallback: Groq LLM provided knowledge ({len(groq_knowledge)} chars)")
            return formatted
            
        except Exception as groq_error:
            logger.error(f"Error in Groq fallback: {str(groq_error)}")
            # Last resort fallback with generic message
            return f"""[FALLBACK: Data for: {query}]

Based on available knowledge:
- Current information and latest updates
- Relevant data points and measurements
- Recent trends and developments
- Current status or conditions

Note: Unable to provide real-time data. 
For live information, please try again later or check a service specific to this topic."""
    
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

CRITICAL INSTRUCTIONS:
1. If the gathered data contains SPECIFIC NUMERICAL VALUES (temperatures, prices, percentages, ranges), YOU MUST include those exact numbers in your synthesis
2. Do NOT convert or generalize numbers - preserve them exactly as they appear
3. Include units (°C, USD, %, etc.) with all numerical values
4. Directly answer the user's query with concrete data

Create a comprehensive 2-3 paragraph research synthesis that:
1. Directly answers the user's query with SPECIFIC VALUES when available
2. Provides clear, actionable information including any numbers from the data
3. Combines data sources appropriately
4. Explains key insights and implications

IMPORTANT: If the query asks for specific numbers (temperature, price, etc.), your synthesis MUST include those numbers."""
        
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
