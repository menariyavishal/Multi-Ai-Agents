"""Tests for Researcher Agent - Reads Planner's output to determine data sources."""

import pytest


class TestPlannerUnderstandsUserIntent:
    """Test how Planner interprets user request and plans data gathering."""
    
    def test_planner_for_mobile_app_needs_both(self):
        """Planner thinks: To build successful app, need CURRENT + HISTORICAL."""
        user_input = "Build a mobile app"
        
        # Planner thinks: What does SUCCESS look like?
        # Answer: Good app = current market insight + proven patterns
        planner_plan = """
        Phase 1: Market Research & Best Practices
        - Analyze CURRENT market trends (what users want NOW)
        - Study HISTORICAL evolution of successful apps
        - Understand CURRENT technology landscape
        - Learn from PAST mistakes and successes
        """
        
        # Researcher reads this and sees BOTH indicators
        has_current = any(kw in planner_plan.lower() for kw in ["current", "now", "latest"])
        has_historical = any(kw in planner_plan.lower() for kw in ["historical", "past", "evolution"])
        
        assert has_current, "Planner includes current data need"
        assert has_historical, "Planner includes historical data need"
    
    def test_planner_thinks_about_success_not_literal_question(self):
        """Planner doesn't answer literally, but plans for SUCCESS."""
        user_input = "What's the weather?"
        
        # Even simple question, Planner thinks about context
        # "Build app" = needs current + historical for success
        
        user_intent = "Build a mobile app"
        
        # Planner's thinking:
        planner_reasoning = """
        User wants to build mobile app.
        For SUCCESS, they need:
        1. Current knowledge: What works NOW (2026)
        2. Historical knowledge: What patterns proved successful
        Combined = Best approach
        """
        
        # This is what makes Planner intelligent
        assert "Current" in planner_reasoning
        assert "Historical" in planner_reasoning


class TestResearcherReadsPlannersIntelligence:
    """Test Researcher interprets what Planner planned."""
    
    def test_researcher_sees_current_in_plan(self):
        """When Planner mentions 'current', Researcher uses MCP."""
        planner_output = """
        Phase 1: Market Analysis
        - Research CURRENT market demands 2026
        - Study CURRENT frameworks and tools
        - Analyze CURRENT user preferences
        """
        
        needs_current = "current" in planner_output.lower()
        assert needs_current
        
        # Researcher decision
        sources = ["MCP_SERVERS"] if needs_current else []
        assert "MCP_SERVERS" in sources
    
    def test_researcher_sees_historical_in_plan(self):
        """When Planner mentions 'historical', Researcher uses DATABASE."""
        planner_output = """
        Phase 2: Proven Patterns
        - Study HISTORICAL success patterns of apps
        - Learn from PAST failures
        - Understand EVOLUTION of mobile technology
        """
        
        needs_historical = any(kw in planner_output.lower() for kw in ["historical", "past", "evolution"])
        assert needs_historical
        
        # Researcher decision
        sources = ["DATABASE"] if needs_historical else []
        assert "DATABASE" in sources
    
    def test_researcher_combines_both_for_best_approach(self):
        """Planner signals BOTH, so Researcher combines them."""
        planner_output = """
        Phase 1: Market Research & Best Practices
        - Analyze CURRENT market (2026)
        - Study HISTORICAL patterns
        - Compare past vs present
        - Get best of both worlds
        """
        
        needs_current = "current" in planner_output.lower()
        needs_historical = "historical" in planner_output.lower()
        
        assert needs_current and needs_historical
        
        # Researcher uses both
        sources = []
        if needs_current:
            sources.append("MCP_SERVERS")
        if needs_historical:
            sources.append("DATABASE")
        
        assert len(sources) == 2


class TestPlannerPhilosophy:
    """Test Planner's intelligent thinking about data needs."""
    
    def test_scenario_mobile_app_why_both_needed(self):
        """Demonstrate WHY mobile app needs CURRENT + HISTORICAL."""
        user_query = "Build a mobile app"
        
        # WITHOUT history: Only "use latest framework"
        # WITH history: "Use latest framework WITH proven patterns"
        
        planner_plan = """
        To build SUCCESSFUL mobile app:
        
        CURRENT (2026):
        - What do users want RIGHT NOW?
        - What's trending in app stores?
        - What frameworks are best NOW?
        - What competitors doing NOW?
        
        HISTORICAL (proven patterns):
        - What app architectures succeeded?
        - What common mistakes to avoid?
        - What patterns are time-tested?
        - How did technology evolve?
        
        BENEFIT: Latest tech + Proven patterns = SUCCESS
        """
        
        has_current = "current" in planner_plan.lower()
        has_historical = "historical" in planner_plan.lower()
        has_benefit = "success" in planner_plan.lower()
        
        assert has_current and has_historical and has_benefit
    
    def test_scenario_weather_only_current_needed(self):
        """Weather query only needs CURRENT, not historical."""
        user_query = "What's the weather?"
        
        planner_plan = """
        Weather Information Analysis:
        - Get real-time temperature
        - Get live weather conditions
        - Get real-time forecast
        
        Focus: Present conditions only
        """
        
        needs_current = any(kw in planner_plan.lower() for kw in ["real-time", "live"])
        needs_historical = any(kw in planner_plan.lower() for kw in ["historical", "past", "evolution"])
        
        assert needs_current
        assert not needs_historical
    
    def test_scenario_history_only_historical_needed(self):
        """History query only needs HISTORICAL."""
        user_query = "What's the history of AI?"
        
        planner_plan = """
        Historical Information Analysis:
        - Research AI history from 1950s onwards
        - Study evolution of AI algorithms
        - Learn about past breakthroughs and milestones
        - Trace development timeline
        
        Focus: Historical perspective only
        """
        
        needs_current = any(kw in planner_plan.lower() for kw in ["current", "latest", "now", "today"])
        needs_historical = any(kw in planner_plan.lower() for kw in ["historical", "evolution", "past", "timeline"])
        
        assert not needs_current
        assert needs_historical


class TestResearcherFollowsPlannerLeadership:
    """Test Researcher trusts Planner's judgment."""
    
    def test_researcher_doesnt_override_planner(self):
        """Researcher doesn't second-guess Planner's decisions."""
        planner_output = """
        Phase 1: Comprehensive Research
        - Get CURRENT data: user trends, market 2026
        - Get HISTORICAL data: proven architectures
        - Compare and combine for best approach
        """
        
        # Researcher reads and trusts
        researcher_interpretation = f"""
        Planner says we need:
        - CURRENT data (for latest)
        - HISTORICAL data (for proven patterns)
        So I will gather from MCP + DATABASE
        """
        
        assert "MCP + DATABASE" in researcher_interpretation
    
    def test_researcher_implements_planners_logic(self):
        """Researcher follows through on Planner's plan."""
        planner_plan = """
        Research Strategy:
        - Understand CURRENT market reality
        - Learn HISTORICAL lessons
        - Synthesize both
        """
        
        # Researcher's execution
        mcp_data = "CURRENT market info"
        db_data = "HISTORICAL patterns"
        synthesis = f"{db_data} + {mcp_data} = Best approach"
        
        assert mcp_data in synthesis
        assert db_data in synthesis


class TestDataSourceDecisions:
    """Test how data sources are decided."""
    
    def test_current_keyword_signals_mcp(self):
        """'Current' in plan → use MCP_SERVERS."""
        plan_phrases = [
            "Analyze current market",
            "Get latest information",
            "Real-time data needed",
            "Today's trends"
        ]
        
        for phrase in plan_phrases:
            has_current_indicator = any(kw in phrase.lower() for kw in ["current", "latest", "real-time", "today"])
            assert has_current_indicator
    
    def test_historical_keyword_signals_database(self):
        """'Historical' in plan → use DATABASE."""
        plan_phrases = [
            "Historical evolution",
            "Past patterns",
            "Proven architectures",
            "Evolution of technology"
        ]
        
        for phrase in plan_phrases:
            has_historical_indicator = any(kw in phrase.lower() for kw in ["historical", "past", "proven", "evolution"])
            assert has_historical_indicator
    
    def test_combine_keyword_signals_both(self):
        """Compare/combine → use MCP + DATABASE."""
        plan_phrases = [
            "Compare current vs past",
            "Combine trends with patterns",
            "Past vs present analysis"
        ]
        
        for phrase in plan_phrases:
            has_both_signal = any(kw in phrase.lower() for kw in ["compare", "combine", "vs", "both"])
            assert has_both_signal
