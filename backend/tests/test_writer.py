"""Test cases for Writer agent."""

import pytest
from app.agents.writer import Writer


@pytest.fixture
def writer(groq_api_key):
    """Create writer instance for testing."""
    if not groq_api_key:
        pytest.skip("GROQ_API_KEY not set")
    return Writer()


@pytest.fixture
def mock_state():
    """Create mock workflow state with analysis."""
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
Combining real-time and historical data shows sustainable growth pattern.""",
        "analysis": {
            "patterns": ["Growth trend identified", "Market consolidation observed"],
            "statistics": {
                "total_words": 250,
                "total_sentences": 15,
                "data_coverage_percentage": 75.0,
                "data_sources": 2
            },
            "insights": [
                "AI market showing sustained growth",
                "Major players dominating industry",
                "Technology accessibility improving"
            ],
            "recommendations": [
                "Invest in AI infrastructure",
                "Monitor market consolidation",
                "Track emerging technologies"
            ],
            "confidence_level": 0.85,
            "data_quality": "high"
        },
        "iteration": 1,
        "messages": []
    }


def test_writer_initialization(writer):
    """Test Writer initialization."""
    assert writer.agent_role == "writer"
    assert writer.llm is not None


def test_writer_call_with_analysis(writer, mock_state):
    """Test Writer synthesizing analysis into draft."""
    result = writer.call(mock_state)
    
    # Verify state is passed through
    assert "draft" in result
    assert result["writer_complete"] is True
    assert result["query"] == mock_state["query"]
    
    # Verify draft has content
    draft = result["draft"]
    assert len(draft) > 0
    assert isinstance(draft, str)


def test_writer_call_without_query(writer, mock_state):
    """Test Writer handles missing query gracefully."""
    mock_state["query"] = ""
    result = writer.call(mock_state)
    
    assert result["writer_complete"] is True
    assert result["draft"] == ""


def test_extract_key_information(writer):
    """Test key information extraction."""
    analysis = {
        "patterns": ["Pattern 1", "Pattern 2", "Pattern 3"],
        "insights": ["Insight A", "Insight B"],
        "confidence_level": 0.9
    }
    
    info = writer._extract_key_information(analysis)
    
    assert isinstance(info, list)
    assert len(info) > 0
    assert any(item["type"] == "pattern" for item in info)
    assert any(item["type"] == "insight" for item in info)
    assert any(item["type"] == "confidence" for item in info)


def test_create_executive_summary(writer):
    """Test executive summary creation."""
    query = "Test query"
    analysis = {
        "patterns": ["p1", "p2", "p3"],
        "insights": ["i1", "i2"],
        "confidence_level": 0.8,
        "data_quality": "high"
    }
    
    summary = writer._create_executive_summary(query, analysis)
    
    assert "Executive Summary" in summary
    assert query in summary
    assert "3" in summary  # patterns count
    assert "2" in summary  # insights count
    assert "80%" in summary  # confidence
    assert "HIGH" in summary  # data quality


def test_write_recommendations(writer):
    """Test recommendations section writing."""
    recommendations = [
        "Recommendation 1: Invest in infrastructure",
        "Recommendation 2: Monitor trends",
        "Consider: Expand market reach"
    ]
    insights = ["Insight 1", "Insight 2"]
    
    section = writer._write_recommendations(recommendations, insights)
    
    assert "Recommendations" in section
    assert len(section) > 0
    assert "1." in section
    assert "2." in section
    assert "3." in section


def test_write_recommendations_empty(writer):
    """Test recommendations with empty list."""
    section = writer._write_recommendations([], [])
    
    assert "Recommendations" in section
    assert "No specific recommendations" in section


def test_write_conclusion(writer):
    """Test conclusion writing."""
    query = "What are the trends?"
    confidence = 0.85
    data_quality = "high"
    
    conclusion = writer._write_conclusion(query, confidence, data_quality)
    
    assert "Conclusion" in conclusion
    assert query in conclusion
    assert "highly reliable" in conclusion.lower()


def test_write_conclusion_low_quality(writer):
    """Test conclusion with low data quality."""
    conclusion = writer._write_conclusion("Query", 0.3, "low")
    
    assert "Conclusion" in conclusion
    assert "preliminary" in conclusion.lower() or "further" in conclusion.lower()


def test_create_metadata_section(writer):
    """Test metadata section creation."""
    analysis = {
        "patterns": ["p1", "p2"],
        "insights": ["i1", "i2", "i3"],
        "statistics": {
            "total_words": 500,
            "data_coverage_percentage": 85.5,
            "data_sources": 3
        },
        "confidence_level": 0.9,
        "data_quality": "high"
    }
    
    metadata = writer._create_metadata_section(analysis)
    
    assert "Key Findings Overview" in metadata
    assert "Patterns Identified" in metadata
    assert "Key Insights" in metadata
    assert "2" in metadata  # patterns count
    assert "3" in metadata  # insights count
    assert "85.5%" in metadata  # coverage
    assert "High" in metadata  # quality


def test_compile_final_draft(writer):
    """Test final draft compilation."""
    analysis = {
        "patterns": ["Pattern 1"],
        "insights": ["Insight 1"],
        "statistics": {"data_sources": 1, "data_coverage_percentage": 50},
        "confidence_level": 0.7,
        "data_quality": "medium"
    }
    
    query = "Test Query"
    summary = "# Executive Summary\nSummary content"
    body = "Main body content"
    recommendations = "## Recommendations\nRec 1"
    conclusion = "## Conclusion\nConclusion content"
    
    draft = writer._compile_final_draft(
        query, summary, body, recommendations, conclusion, analysis
    )
    
    assert "Comprehensive Analysis Report" in draft
    assert query in draft
    assert "MEDIUM" in draft  # data quality
    assert "70%" in draft  # confidence
    assert "Executive Summary" in draft
    assert "Main body content" in draft
    assert "Recommendations" in draft
    assert "Conclusion" in draft
    assert "Key Findings Overview" in draft
