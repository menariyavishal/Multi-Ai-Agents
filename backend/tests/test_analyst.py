"""Test cases for Analyst agent."""

import pytest
from app.agents.analyst import Analyst
from app.core.mock_llm import MockLLM
from unittest.mock import patch, MagicMock


@pytest.fixture
def analyst(groq_api_key):
    """Create analyst instance for testing."""
    if not groq_api_key:
        pytest.skip("GROQ_API_KEY not set")
    return Analyst()


@pytest.fixture
def mock_state():
    """Create mock workflow state."""
    return {
        "query": "What are the latest AI trends?",
        "plan": "Analyze AI industry trends and market dynamics",
        "research": """[REAL-TIME DATA]
Latest AI trends show rapid advancement in large language models.
Current market growth: 45% YoY in AI sector.

[HISTORICAL DATA]
AI evolution over 5 years shows consistent growth trajectory.
Historical volatility decreased as field matured.

[SYNTHESIS]
Combining real-time and historical data shows sustainable growth pattern.
Field is stabilizing with major players dominating market.""",
        "iteration": 1,
        "messages": []
    }


def test_analyst_initialization(analyst):
    """Test Analyst initialization."""
    assert analyst.agent_role == "analyst"
    assert analyst.llm is not None


def test_analyst_call_with_research(analyst, mock_state):
    """Test Analyst processing research data."""
    result = analyst.call(mock_state)
    
    # Verify state is passed through
    assert "analysis" in result
    assert result["analyst_complete"] is True
    assert result["query"] == mock_state["query"]
    
    # Verify analysis structure
    analysis = result["analysis"]
    assert "patterns" in analysis
    assert "statistics" in analysis
    assert "insights" in analysis
    assert "recommendations" in analysis
    assert "status" in analysis
    assert analysis["status"] == "success"


def test_analyst_call_without_research(analyst, mock_state):
    """Test Analyst handles missing research gracefully."""
    mock_state["research"] = ""
    result = analyst.call(mock_state)
    
    analysis = result["analysis"]
    assert analysis["status"] == "no_data"
    assert len(analysis["patterns"]) == 0
    assert len(analysis["insights"]) == 0


def test_parse_research_data(analyst):
    """Test research data parsing."""
    research = """[REAL-TIME DATA]
Some real-time info

[HISTORICAL DATA]
Historical information

[SYNTHESIS]
Combined findings"""
    
    parsed = analyst._parse_research_data(research)
    
    assert "real_time" in parsed
    assert "historical" in parsed
    assert "synthesis" in parsed
    assert parsed["real_time"] != ""
    assert parsed["historical"] != ""
    assert parsed["synthesis"] != ""


def test_extract_patterns(analyst):
    """Test pattern extraction."""
    parsed_research = {
        "real_time": "growth accelerating rapidly",
        "historical": "consistent increase over years",
        "synthesis": "volatile market conditions",
        "full_text": "All combined"
    }
    
    patterns = analyst._extract_patterns(parsed_research, "test query")
    
    assert isinstance(patterns, list)
    assert len(patterns) > 0


def test_calculate_statistics(analyst):
    """Test statistics calculation."""
    parsed_research = {
        "real_time": "Some real-time data here.",
        "historical": "Historical information available.",
        "synthesis": "Combined analysis results."
    }
    patterns = ["growth", "stability"]
    
    stats = analyst._calculate_statistics(parsed_research, patterns)
    
    assert "total_characters" in stats
    assert "total_words" in stats
    assert "total_sentences" in stats
    assert "patterns_count" in stats
    assert stats["patterns_count"] == 2


def test_assess_data_quality(analyst):
    """Test data quality assessment."""
    parsed_research = {
        "real_time": "Present",
        "historical": "Present",
        "synthesis": "Present"
    }
    patterns = ["growth", "decline", "trend"]
    statistics = {"total_words": 100}
    
    quality = analyst._assess_data_quality(parsed_research, patterns, statistics)
    
    assert "quality_level" in quality
    assert quality["quality_level"] in ["high", "medium", "low"]
    assert "quality_score" in quality
    assert 0 <= quality["quality_score"] <= 1


def test_generate_recommendations(analyst):
    """Test recommendation generation."""
    insights = ["Insight 1", "Insight 2"]
    patterns = ["growth", "trend"]
    data_quality = {"quality_level": "high"}
    
    recommendations = analyst._generate_recommendations(
        insights, patterns, data_quality
    )
    
    assert isinstance(recommendations, list)
    assert len(recommendations) >= 3
    assert all(isinstance(r, str) for r in recommendations)


def test_parse_json_response(analyst):
    """Test JSON response parsing."""
    # Valid JSON response
    response1 = '{"insights": ["insight1"], "confidence_level": 0.9}'
    result1 = analyst._parse_json_response(response1)
    assert result1["confidence_level"] == 0.9
    
    # JSON with extra text
    response2 = 'Some text {"insights": ["insight2"], "confidence_level": 0.8} more text'
    result2 = analyst._parse_json_response(response2)
    assert result2["confidence_level"] == 0.8
    
    # Invalid JSON falls back
    response3 = 'This is not JSON'
    result3 = analyst._parse_json_response(response3)
    assert "insights" in result3
    assert "confidence_level" in result3


def test_create_summary(analyst):
    """Test summary creation."""
    patterns = ["growth", "stability"]
    insights = {"insights": ["Key finding 1", "Key finding 2"]}
    recommendations = ["Rec 1", "Rec 2"]
    
    summary = analyst._create_summary(patterns, insights, recommendations)
    
    assert "ANALYSIS SUMMARY" in summary
    assert "growth" in summary
    assert "Key finding 1" in summary
    assert "Rec 1" in summary
