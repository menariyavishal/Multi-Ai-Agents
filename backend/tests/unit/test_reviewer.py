"""Test cases for Reviewer agent."""

import pytest
from app.agents.reviewer import Reviewer


@pytest.fixture
def reviewer(groq_api_key):
    """Create reviewer instance for testing."""
    if not groq_api_key:
        pytest.skip("GROQ_API_KEY not set")
    return Reviewer()


@pytest.fixture
def mock_state():
    """Create mock workflow state with draft."""
    return {
        "query": "What are the latest AI trends?",
        "draft": """# Comprehensive Analysis Report

**Query:** What are the latest AI trends?

**Report Generated:** Analysis completed with data quality: HIGH

**Analysis Confidence:** 85%

---

## Executive Summary

This comprehensive analysis addresses: **What are the latest AI trends?**

The investigation identified key patterns and insights based on multi-source research and data synthesis.

## Key Findings Overview

| Metric | Value |
|--------|-------|
| Patterns Identified | 2 |
| Key Insights | 3 |
| Data Coverage | 85.0% |
| Data Sources | 3 |
| Confidence Level | 85% |
| Data Quality | High |

The current trends in AI and machine learning show strong growth and innovation. Major advancements include deep learning, natural language processing, and autonomous systems. The analysis reveals sustained market expansion and increasing adoption across industries.

Key patterns demonstrate consistent growth trajectories with multiple emerging opportunities for businesses to leverage AI capabilities. The data quality is high, with comprehensive coverage from reliable sources.

## Recommendations

Based on the analysis, the following actionable recommendations are proposed:

1. **Invest in AI infrastructure development**
2. **Monitor emerging AI technologies closely**
3. **Build team expertise in machine learning**

### Implementation Priority

These 3 recommendations are prioritized based on their impact potential and feasibility.

## Conclusion

This analysis provides evidence-based insights for decision-making. Organizations should implement these recommendations to stay competitive in the evolving AI landscape.

Moving forward, continued monitoring and analysis will ensure strategies remain aligned with market trends.""",
        "analysis": {
            "patterns": ["Growth pattern", "Innovation trend"],
            "statistics": {
                "total_words": 250,
                "data_coverage_percentage": 85.0,
                "data_sources": 3
            },
            "insights": [
                "Strong market growth",
                "Technology accessibility improving",
                "Industry adoption accelerating"
            ],
            "recommendations": [
                "Invest in AI infrastructure",
                "Monitor technologies",
                "Build team expertise"
            ],
            "confidence_level": 0.85,
            "data_quality": "high"
        },
        "plan": "Analyze AI trends",
        "research": "Research on AI trends...",
        "iteration": 1,
        "messages": []
    }


def test_reviewer_initialization(reviewer):
    """Test Reviewer initialization."""
    assert reviewer.agent_role == "reviewer"
    assert reviewer.llm is not None


def test_reviewer_call_with_draft(reviewer, mock_state):
    """Test Reviewer validating draft."""
    result = reviewer.call(mock_state)
    
    # Verify state is passed through
    assert "review_feedback" in result
    assert result["reviewer_complete"] is True
    assert "final_answer" in result


def test_reviewer_call_without_draft(reviewer, mock_state):
    """Test Reviewer handles missing draft gracefully."""
    mock_state["draft"] = ""
    result = reviewer.call(mock_state)
    
    assert result["reviewer_complete"] is True
    assert result["review_feedback"]["recommendation"] == "NEEDS_REVISION"


def test_validate_structure(reviewer):
    """Test structure validation."""
    good_draft = """# Comprehensive Analysis Report

## Executive Summary
Content here.

## Key Findings Overview

| Metric | Value |
|--------|-------|
| Test | 1 |

## Recommendations
Recommendations here.

## Conclusion
Conclusion here."""
    
    issues = reviewer._validate_structure(good_draft)
    assert len(issues) == 0
    
    # Test with missing sections
    bad_draft = "Just some random text without structure."
    bad_issues = reviewer._validate_structure(bad_draft)
    assert len(bad_issues) > 0


def test_assess_content_quality(reviewer):
    """Test content quality assessment."""
    good_content = """This is a comprehensive report addressing the query directly.
    
The analysis shows clear patterns emerging from the data. Multiple sources confirm these findings.

The results demonstrate strong quality and consistency across measurements. 

The recommendations should be considered carefully for implementation.

Overall, the data quality is high and conclusions are well-supported by evidence. Future monitoring is recommended."""
    
    quality = reviewer._assess_content_quality(good_content, "test query")
    assert "rating" in quality
    assert quality["rating"] in ["Excellent", "Good", "Fair", "Poor"]
    assert quality["word_count"] > 0


def test_assess_content_quality_short(reviewer):
    """Test content quality with too-short content."""
    short_content = "Brief text."
    
    quality = reviewer._assess_content_quality(short_content, "test query")
    assert "too short" in str(quality.get("issues", [])).lower()


def test_verify_data_integrity(reviewer):
    """Test data integrity verification."""
    draft = """# Report

The analysis shows 85% confidence level in the findings.

Data quality assessment: HIGH

The key recommendations include:
1. First recommendation
2. Second recommendation"""
    
    analysis = {
        "confidence_level": 0.85,
        "data_quality": "high",
        "recommendations": ["First recommendation", "Second recommendation"],
        "patterns": ["Pattern mentioned here"],
        "insights": ["Insight one", "Insight two"]
    }
    
    issues = reviewer._verify_data_integrity(draft, analysis)
    # Should have minimal issues if data is properly cited
    assert isinstance(issues, list)


def test_check_completeness(reviewer):
    """Test completeness checking."""
    draft = """# Report on AI trends

## Executive Summary
Addressing trends in AI

## Key Findings
Analysis shows growth trends

## Recommendations
Should monitor AI development

## Conclusion
Future focus on AI technology"""
    
    issues = reviewer._check_completeness(draft, "What are trends in AI?", {})
    assert isinstance(issues, list)


def test_calculate_quality_score(reviewer):
    """Test quality score calculation."""
    issues = ["Issue 1", "Issue 2"]
    content_quality = {"rating": "Good"}
    llm_review = {"rating": "Good", "strengths": []}
    
    score = reviewer._calculate_quality_score(issues, content_quality, llm_review)
    
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_score_to_level(reviewer):
    """Test score to level conversion."""
    assert reviewer._score_to_level(0.95) == "Excellent"
    assert reviewer._score_to_level(0.85) == "Good"
    assert reviewer._score_to_level(0.75) == "Fair"
    assert reviewer._score_to_level(0.60) == "Poor"
    assert reviewer._score_to_level(0.30) == "Critical"


def test_make_routing_decision(reviewer):
    """Test routing decision logic."""
    # High score, few issues = PASS
    decision1 = reviewer._make_routing_decision(0.85, ["Issue1"])
    assert decision1 == "PASS"
    
    # Low score or many issues = NEEDS_REVISION
    decision2 = reviewer._make_routing_decision(0.70, ["I1", "I2", "I3", "I4"])
    assert decision2 == "NEEDS_REVISION"


def test_parse_json_response(reviewer):
    """Test JSON response parsing."""
    # Valid JSON
    response1 = '{"rating": "Good", "issues": ["issue1"]}'
    result1 = reviewer._parse_json_response(response1)
    assert result1["rating"] == "Good"
    
    # JSON with extra text
    response2 = 'Some text {"rating": "Excellent"} more text'
    result2 = reviewer._parse_json_response(response2)
    assert result2["rating"] == "Excellent"
    
    # Invalid JSON
    response3 = "Not JSON at all"
    result3 = reviewer._parse_json_response(response3)
    assert "rating" in result3


def test_generate_feedback(reviewer):
    """Test feedback generation."""
    structure_issues = ["Missing section"]
    content_quality = {"rating": "Good", "issues": []}
    integrity_issues = []
    completeness_issues = ["Could be more thorough"]
    llm_review = {
        "rating": "Good",
        "assessment": "Well written",
        "strengths": ["Clear structure"],
        "issues": []
    }
    
    feedback = reviewer._generate_feedback(
        structure_issues,
        content_quality,
        integrity_issues,
        completeness_issues,
        llm_review,
        0.82
    )
    
    assert "feedback_items" in feedback
    assert len(feedback["feedback_items"]) > 0
    assert "summary" in feedback
