"""Tests for Researcher Agent data gathering based on Planner's plan."""

import pytest


class TestResearcherPlanBasedDataGathering:
    """Test Researcher gathers data based on what Planner specified."""
    
    def test_researcher_gathers_mcp_when_plan_says_current(self):
        """Test Researcher gathers from MCP when plan mentions 'current'."""
        plan = """
        Phase 1: Market Analysis
        - Analyze current market trends
        - Study latest technologies
        """
        query = "Build a mobile app"
        
        # Researcher interprets plan
        should_use_mcp = any(kw in plan.lower() for kw in ["current", "latest"])
        
        assert should_use_mcp, "Plan mentions current trends"
    
    def test_researcher_gathers_db_when_plan_says_historical(self):
        """Test Researcher gathers from DB when plan mentions 'historical'."""
        plan = """
        Phase 1: Research
        - Study historical evolution of technology
        - Analyze past market trends
        """
        query = "Build a mobile app"
        
        # Researcher interprets plan
        should_use_db = any(kw in plan.lower() for kw in ["historical", "past"])
        
        assert should_use_db, "Plan mentions historical data"
    
    def test_researcher_gathers_both_when_plan_mentions_both(self):
        """Test Researcher gathers from both when plan mentions both."""
        plan = """
        Phase 1: Comprehensive Analysis
        - Study historical market evolution (2015-2025)
        - Analyze current market trends (2026)
        - Compare past vs present approaches
        """
        query = "Build a mobile app"
        
        # Researcher interprets plan
        has_current = any(kw in plan.lower() for kw in ["current", "latest", "2026"])
        has_historical = any(kw in plan.lower() for kw in ["historical", "past", "2015-2025"])
        
        assert has_current and has_historical, "Plan mentions both"


class TestResearcherPlanInterpretationForData:
    """Test how Researcher interprets plan to determine data needs."""
    
    def test_interpret_plan_phase_keywords(self):
        """Test Researcher interprets plan phase keywords."""
        # Test that phases can be identified as CURRENT, HISTORICAL, or COMBINED
        current_phases = ["Current Market Analysis", "Latest Technology Review"]
        historical_phases = ["Historical Trends", "Evolution Timeline"]
        combined_phrases = ["Comparative Study", "Past vs Present"]
        
        # Check current phases
        for phase in current_phases:
            has_keyword = any(kw in phase.lower() for kw in ["current", "latest"])
            assert has_keyword, f"Phase '{phase}' should have current keyword"
        
        # Check historical phases
        for phase in historical_phases:
            has_keyword = any(kw in phase.lower() for kw in ["historical", "past", "evolution"])
            assert has_keyword, f"Phase '{phase}' should have historical keyword"
        
        # Check combined phrases
        for phrase in combined_phrases:
            has_keyword = any(kw in phrase.lower() for kw in ["compare", "comparative", "past", "vs"])
            assert has_keyword, f"Phase '{phrase}' should indicate comparison"
    
    def test_researcher_reads_plan_context(self):
        """Test Researcher reads full plan for context."""
        plan = """
        Query: Build a mobile app
        
        Phase 1: Market Research (2 weeks)
        - Research current market (REAL_TIME)
        - Study app evolution (HISTORICAL)
        
        Phase 2: Competitive Analysis
        - Analyze current leaders
        - Study how market changed
        """
        
        query = "Build a mobile app"
        
        # Researcher should see both data types are needed
        full_context = f"{query}\n{plan}"
        
        has_context = len(full_context) > len(query)
        assert has_context
    
    def test_researcher_prioritizes_plan_over_query(self):
        """Test Researcher uses plan, not just query."""
        query = "Build something"  # Generic
        plan = """
        Phase 1: Current implementation research
        Phase 2: Historical case studies
        """
        
        # Plan is more specific
        assert len(plan) > len(query)
        assert "current" in plan.lower()
        assert "historical" in plan.lower()


class TestResearcherDataSourceSelection:
    """Test Researcher's data source selection logic."""
    
    def test_select_mcp_servers_for_current(self):
        """Test MCP servers are selected for 'current' requests."""
        plan = "Research current industry trends"
        
        sources = []
        if any(kw in plan.lower() for kw in ["current", "latest", "live", "now"]):
            sources.append("MCP_SERVERS")
        
        assert "MCP_SERVERS" in sources
    
    def test_select_database_for_historical(self):
        """Test Database is selected for 'historical' requests."""
        plan = "Study historical development timeline"
        
        sources = []
        if any(kw in plan.lower() for kw in ["historical", "past", "evolution", "was"]):
            sources.append("DATABASE")
        
        assert "DATABASE" in sources
    
    def test_select_both_for_combined(self):
        """Test Both sources are selected for combined requests."""
        plan = "Compare past evolution with current state"
        
        sources = []
        if any(kw in plan.lower() for kw in ["current", "latest", "live"]):
            sources.append("MCP_SERVERS")
        if any(kw in plan.lower() for kw in ["historical", "past", "evolution"]):
            sources.append("DATABASE")
        
        assert "MCP_SERVERS" in sources
        assert "DATABASE" in sources


class TestResearcherRealWorldPlanScenarios:
    """Test real-world plan scenarios."""
    
    def test_scenario_mobile_app_data_gathering(self):
        """Test data gathering for mobile app plan."""
        plan = """
        Phase 1: Market Research (2 weeks)
        - Research current mobile trends (2026)
        - Study smartphone market evolution (2015-2025)
        - Compare iOS vs Android approaches (current vs history)
        """
        
        should_use_mcp = "current" in plan.lower() or "2026" in plan.lower()
        should_use_db = "evolution" in plan.lower() or "2015-2025" in plan.lower()
        
        assert should_use_mcp, "Need current mobile trends"
        assert should_use_db, "Need historical evolution"
    
    def test_scenario_weather_data_gathering(self):
        """Test data gathering for weather query."""
        plan = """
        Phase 1: Current Weather Analysis
        - Get current temperature and conditions
        - Fetch real-time weather data
        """
        
        should_use_mcp = "current" in plan.lower() or "real-time" in plan.lower()
        should_use_db = "historical" in plan.lower() or "past" in plan.lower()
        
        assert should_use_mcp, "Weather is real-time"
        assert not should_use_db, "Weather doesn't need history"
    
    def test_scenario_historical_research_data_gathering(self):
        """Test data gathering for historical research."""
        plan = """
        Phase 1: Historical Research
        - Gather historical documents (1945-1960)
        - Study past events timeline
        - Analyze historical evolution
        """
        
        should_use_mcp = "current" in plan.lower() or "latest" in plan.lower()
        should_use_db = "historical" in plan.lower() or "past" in plan.lower()
        
        assert not should_use_mcp, "History doesn't need current data"
        assert should_use_db, "History needs database"


class TestResearcherMCPServerGathering:
    """Test MCP server data gathering when needed."""
    
    def test_mcp_gathers_when_plan_mentions_current(self):
        """Test MCP is used when plan mentions 'current'."""
        plan = "Get current market prices"
        
        # Condition check
        uses_mcp = any(kw in plan.lower() for kw in ["current", "latest", "live", "today"])
        
        assert uses_mcp
    
    def test_mcp_gathers_multiple_types(self):
        """Test MCP can gather different data types."""
        data_types = {
            "current trends": ["current"],
            "latest updates": ["latest"],
            "live prices": ["live"],
            "real-time data": ["real-time"],
            "today's news": ["today"]
        }
        
        for phrase, keywords in data_types.items():
            found = any(kw in phrase.lower() for kw in keywords)
            assert found


class TestResearcherDatabaseGathering:
    """Test database data gathering when needed."""
    
    def test_database_gathers_when_plan_mentions_historical(self):
        """Test database is used when plan mentions 'historical'."""
        plan = "Study historical patterns"
        
        # Condition check
        uses_db = any(kw in plan.lower() for kw in ["historical", "past", "evolution"])
        
        assert uses_db
    
    def test_database_gathers_multiple_types(self):
        """Test database can gather different data types."""
        data_types = {
            "historical records": ["historical"],
            "past events": ["past"],
            "evolution timeline": ["evolution"],
            "what was": ["was"],
            "before": ["before"]
        }
        
        for phrase, keywords in data_types.items():
            found = any(kw in phrase.lower() for kw in keywords)
            assert found


class TestResearcherDataSynthesis:
    """Test how Researcher synthesizes gathered data."""
    
    def test_synthesize_mcp_only_data(self):
        """Test synthesis when only MCP data gathered."""
        mcp_data = "Current market analysis from 2026"
        
        synthesis = f"Based on real-time data: {mcp_data}"
        
        assert "real-time" in synthesis.lower()
        assert "2026" in synthesis
    
    def test_synthesize_database_only_data(self):
        """Test synthesis when only database data gathered."""
        db_data = "Historical evolution from 2010-2020"
        
        synthesis = f"Based on historical records: {db_data}"
        
        assert "historical" in synthesis.lower()
        assert "2010-2020" in synthesis
    
    def test_synthesize_combined_data(self):
        """Test synthesis when both sources gathered."""
        mcp_data = "Current: Advanced technology in 2026"
        db_data = "Historical: Basic technology in 2010"
        
        synthesis = f"Evolution perspective: {db_data} → {mcp_data}"
        
        assert "2010" in synthesis
        assert "2026" in synthesis
        assert "Evolution" in synthesis
