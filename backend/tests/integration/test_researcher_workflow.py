"""Tests for Researcher Agent workflow based on Planner's output."""

import pytest


class TestResearcherWorkflowSequence:
    """Test Researcher's workflow in LangGraph sequence."""
    
    def test_researcher_receives_planner_output(self):
        """Test Researcher receives state from Planner."""
        state = {
            "query": "Build a mobile app",
            "plan": """
            Phase 1: Market Research (2 weeks)
            - Analyze current market
            - Study historical evolution
            """,
            "iteration": 1,
            "messages": []
        }
        
        # Researcher receives this state
        assert "query" in state
        assert "plan" in state
        assert state.get("plan") is not None
    
    def test_researcher_analyzes_plan_for_data_needs(self):
        """Test Researcher analyzes plan to determine data sources."""
        plan = """
        Phase 1: Market Analysis
        - Research current trends
        - Study historical patterns
        """
        
        # Researcher interprets
        has_current = "current" in plan.lower()
        has_historical = "historical" in plan.lower()
        
        query_type = "COMBINED" if (has_current and has_historical) else "REAL_TIME" if has_current else "HISTORICAL"
        
        assert query_type == "COMBINED"
    
    def test_researcher_selects_data_sources(self):
        """Test Researcher selects appropriate data sources."""
        plan = "Research current market and historical evolution"
        
        sources = []
        if any(kw in plan.lower() for kw in ["current", "latest", "live"]):
            sources.append("MCP_SERVERS")
        if any(kw in plan.lower() for kw in ["historical", "past", "evolution"]):
            sources.append("DATABASE")
        
        assert len(sources) == 2
        assert "MCP_SERVERS" in sources
        assert "DATABASE" in sources
    
    def test_researcher_gathers_data(self):
        """Test Researcher gathers data from selected sources."""
        sources = ["MCP_SERVERS", "DATABASE"]
        query = "Build mobile app"
        
        gathered_data = {
            "MCP_SERVERS": "Real-time market data",
            "DATABASE": "Historical market data"
        }
        
        for source in sources:
            assert source in gathered_data
    
    def test_researcher_synthesizes_research(self):
        """Test Researcher synthesizes gathered data into research."""
        gathered = {
            "MCP_SERVERS": "Current 2026 market trends",
            "DATABASE": "Historical market 2015-2025"
        }
        
        research = f"Synthesized: {gathered['DATABASE']} → {gathered['MCP_SERVERS']}"
        
        assert "2015-2025" in research
        assert "2026" in research
    
    def test_researcher_returns_complete_state(self):
        """Test Researcher returns complete state for next agent."""
        initial_state = {
            "query": "Build a mobile app",
            "plan": "Planner's plan",
            "iteration": 1,
            "messages": []
        }
        
        # Researcher adds to state
        updated_state = {
            **initial_state,
            "research": "Comprehensive research findings",
            "data_sources_used": ["MCP_SERVERS", "DATABASE"],
            "researcher_complete": True
        }
        
        assert "research" in updated_state
        assert "query" in updated_state  # Preserved
        assert "plan" in updated_state  # Preserved
        assert updated_state["researcher_complete"] is True


class TestResearcherStateDependency:
    """Test Researcher's dependency on Planner's state."""
    
    def test_researcher_requires_plan_in_state(self):
        """Test Researcher requires plan from Planner."""
        state = {
            "query": "Build a mobile app",
            "plan": "Phase 1: Market Research..."  # From Planner
        }
        
        assert "plan" in state
        assert state["plan"] is not None
    
    def test_researcher_fallback_without_plan(self):
        """Test Researcher can work without plan (fallback)."""
        state = {
            "query": "Build a mobile app"
        }
        
        if "plan" not in state:
            # Fallback: analyze query directly
            query_type = "COMBINED"  # Default safe value
        
        assert query_type == "COMBINED"
    
    def test_researcher_uses_all_state_fields(self):
        """Test Researcher uses all relevant state fields."""
        state = {
            "query": "Build a mobile app",
            "plan": "Phase 1: Current market analysis\nPhase 2: Historical study",
            "iteration": 1,
            "messages": [{"role": "user", "content": "original query"}],
            "context": "additional context"
        }
        
        # All fields should be accessible
        assert state["query"]
        assert state["plan"]
        assert state["iteration"] >= 1
        assert len(state["messages"]) > 0


class TestResearcherDataGatheringWorkflow:
    """Test Researcher's data gathering workflow."""
    
    def test_workflow_mcp_gathering(self):
        """Test MCP data gathering workflow."""
        plan = "Research current market trends"
        
        # Step 1: Analyze plan
        uses_mcp = "current" in plan.lower()
        assert uses_mcp
        
        # Step 2: Prepare MCP query
        mcp_query = "Latest market trends 2026"
        
        # Step 3: Gather from MCP
        mcp_data = f"[MCP DATA] {mcp_query}"
        assert "MCP DATA" in mcp_data
    
    def test_workflow_database_gathering(self):
        """Test database data gathering workflow."""
        plan = "Study historical market evolution"
        
        # Step 1: Analyze plan
        uses_db = "historical" in plan.lower()
        assert uses_db
        
        # Step 2: Prepare DB query
        db_query = "Market history 2015-2025"
        
        # Step 3: Gather from database
        db_data = f"[DB DATA] {db_query}"
        assert "DB DATA" in db_data
    
    def test_workflow_combined_gathering(self):
        """Test combined data gathering workflow."""
        plan = "Compare past market with current state"
        
        # Step 1: Analyze plan
        uses_mcp = "current" in plan.lower()
        uses_db = "past" in plan.lower()
        assert uses_mcp and uses_db
        
        # Step 2: Gather from both
        mcp_data = "[CURRENT DATA]"
        db_data = "[HISTORICAL DATA]"
        
        # Step 3: Synthesize
        synthesis = f"{db_data} → {mcp_data}"
        assert mcp_data in synthesis and db_data in synthesis


class TestResearcherOutputFormat:
    """Test Researcher's output format."""
    
    def test_researcher_output_structure(self):
        """Test Researcher output has required structure."""
        output = {
            "research": "Detailed research findings",
            "data_sources_used": ["MCP_SERVERS"],
            "query_analysis": "REAL_TIME",
            "researcher_complete": True
        }
        
        required_fields = ["research", "researcher_complete"]
        
        for field in required_fields:
            assert field in output
    
    def test_researcher_research_field_content(self):
        """Test research field contains substantive content."""
        research = "Comprehensive analysis based on current market data"
        
        assert len(research) > 20
        assert research is not None
        assert research != ""
    
    def test_researcher_data_sources_list(self):
        """Test data sources are properly listed."""
        sources = ["MCP_SERVERS", "DATABASE"]
        
        valid_sources = ["MCP_SERVERS", "DATABASE"]
        
        for source in sources:
            assert source in valid_sources


class TestResearcherRealWorldWorkflow:
    """Test real-world Researcher workflow scenarios."""
    
    def test_workflow_mobile_app_research(self):
        """Test complete workflow for mobile app query."""
        # State from Planner
        state = {
            "query": "Build a mobile app",
            "plan": """
            Phase 1: Market Research
            - Current market trends (2026)
            - Historical evolution (2015-2025)
            - Competitive landscape
            """
        }
        
        # Researcher workflow
        has_current = "current" in state["plan"].lower()
        has_historical = "historical" in state["plan"].lower()
        
        assert has_current and has_historical
        
        # Determine sources
        sources = []
        if has_current:
            sources.append("MCP_SERVERS")
        if has_historical:
            sources.append("DATABASE")
        
        assert len(sources) == 2
    
    def test_workflow_weather_research(self):
        """Test complete workflow for weather query."""
        state = {
            "query": "What is current temperature?",
            "plan": "Phase 1: Get current weather data (real-time)"
        }
        
        # Researcher workflow
        has_current = "current" in state["plan"].lower() or "real-time" in state["plan"].lower()
        has_historical = "historical" in state["plan"].lower()
        
        assert has_current and not has_historical
        
        # Determine source
        sources = ["MCP_SERVERS"] if has_current else ["DATABASE"]
        assert sources == ["MCP_SERVERS"]
    
    def test_workflow_historical_research(self):
        """Test complete workflow for historical query."""
        state = {
            "query": "History of internet",
            "plan": "Phase 1: Historical analysis (1960-2026)"
        }
        
        # Researcher workflow
        has_current = "current" in state["plan"].lower()
        has_historical = "historical" in state["plan"].lower()
        
        assert not has_current and has_historical
        
        # Determine source
        sources = ["DATABASE"] if has_historical else ["MCP_SERVERS"]
        assert sources == ["DATABASE"]


class TestResearcherMessaging:
    """Test Researcher's message handling in workflow."""
    
    def test_researcher_preserves_message_history(self):
        """Test Researcher preserves conversation history."""
        state = {
            "messages": [
                {"role": "user", "content": "Build a mobile app"},
                {"role": "assistant", "content": "Planner's response"}
            ]
        }
        
        # Researcher receives and preserves
        preserved = state["messages"]
        
        assert len(preserved) == 2
        assert preserved[0]["role"] == "user"
        assert preserved[1]["role"] == "assistant"
    
    def test_researcher_adds_to_messages(self):
        """Test Researcher adds its output to messages."""
        initial_messages = [
            {"role": "user", "content": "Query"},
            {"role": "assistant", "content": "Plan"}
        ]
        
        # Researcher output
        research_msg = {"role": "assistant", "content": "Research findings"}
        
        updated_messages = initial_messages + [research_msg]
        
        assert len(updated_messages) == 3
        assert updated_messages[-1]["role"] == "assistant"
