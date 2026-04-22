"""Analyst Agent - Analyzes Researcher findings and extracts patterns, statistics, and insights."""

import json
import re
from typing import Any, Dict, List
from app.agents.base import BaseAgent
from app.core.logger import get_logger

logger = get_logger(__name__)


class Analyst(BaseAgent):
    """Analyst agent that processes research findings and generates structured analysis."""
    
    def __init__(self):
        """Initialize Analyst agent with Groq qwen/qwen3-32b LLM."""
        super().__init__(agent_role="analyst")
    
    def call(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Researcher's findings and extract patterns, statistics, and insights.
        
        Args:
            state: Workflow state containing:
                - query: The user's original query
                - plan: The Planner's detailed plan
                - research: The Researcher's gathered findings
                - iteration: Current iteration number
                - messages: Message history
        
        Returns:
            Updated state with:
                - analysis: Structured analysis results
                - analyst_complete: True
                - messages: Updated with analysis summary
        """
        query = state.get("query", "")
        plan = state.get("plan", "")
        research = state.get("research", "")
        iteration = state.get("iteration", 1)
        messages = state.get("messages", [])
        
        if not research:
            logger.warning("No research data provided to Analyst")
            return {
                **state,
                "analysis": {
                    "patterns": [],
                    "statistics": {},
                    "insights": [],
                    "recommendations": [],
                    "confidence_level": 0.0,
                    "data_quality": "unavailable",
                    "status": "no_data"
                },
                "analyst_complete": True,
                "messages": messages
            }
        
        logger.info(f"Analyst processing research findings (iteration {iteration})")
        
        # Get data classification from state (from Researcher's analysis)
        data_classification = state.get("data_classification", "COMBINED")  # Default to COMBINED
        logger.info(f"Data classification: {data_classification}")
        
        try:
            # Step 1: Validate and parse research data
            parsed_research = self._parse_research_data(research)
            logger.info(f"Research data parsed: {len(parsed_research)} sections identified")
            
            # Step 2: Extract patterns and trends
            patterns = self._extract_patterns(parsed_research, query)
            logger.info(f"Patterns extracted: {len(patterns)} patterns identified")
            
            # Step 3: Calculate statistics and metrics
            statistics = self._calculate_statistics(parsed_research, patterns)
            logger.info(f"Statistics calculated: {len(statistics)} metrics computed")
            
            # Step 4: Generate insights using LLM
            insights = self._generate_insights(
                query,
                plan,
                parsed_research,
                patterns,
                statistics
            )
            logger.info(f"Insights generated: {len(insights['insights'])} insights, confidence: {insights['confidence_level']}")
            
            # Step 5: Assess data quality (now query-aware based on classification)
            data_quality = self._assess_data_quality(parsed_research, patterns, statistics, data_classification)
            logger.info(f"Data quality assessed: {data_quality['quality_level']}")
            
            # Step 6: Generate recommendations
            recommendations = self._generate_recommendations(
                insights['insights'],
                patterns,
                data_quality
            )
            logger.info(f"Recommendations generated: {len(recommendations)} recommendations")
            
            # Compile final analysis
            analysis = {
                "patterns": patterns,
                "statistics": statistics,
                "insights": insights["insights"],
                "confidence_level": insights["confidence_level"],
                "recommendations": recommendations,
                "data_quality": data_quality["quality_level"],
                "data_quality_details": data_quality["details"],
                "analysis_summary": self._create_summary(patterns, insights, recommendations),
                "status": "success"
            }
            
            return {
                **state,
                "analysis": analysis,
                "analyst_complete": True,
                "messages": messages + [
                    {
                        "role": "assistant",
                        "content": f"Analysis: {len(patterns)} patterns, {len(insights['insights'])} insights, confidence: {insights['confidence_level']:.0%}"
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in Analyst: {str(e)}")
            return {
                **state,
                "analysis": {
                    "patterns": [],
                    "statistics": {},
                    "insights": [],
                    "recommendations": [],
                    "confidence_level": 0.0,
                    "data_quality": "error",
                    "error": str(e),
                    "status": "failed"
                },
                "analyst_complete": True,
                "messages": messages
            }
    
    def _parse_research_data(self, research: str) -> Dict[str, str]:
        """Parse research data into structured sections.
        
        Args:
            research: Raw research findings text
        
        Returns:
            Dictionary with parsed sections
        """
        parsed = {
            "full_text": research,
            "real_time": "",
            "historical": "",
            "synthesis": ""
        }
        
        # Extract real-time section
        rt_match = re.search(r'\[REAL-TIME.*?\](.*?)(?=\[|$)', research, re.DOTALL | re.IGNORECASE)
        if rt_match:
            parsed["real_time"] = rt_match.group(1).strip()
        
        # Extract historical section
        hist_match = re.search(r'\[HISTORICAL.*?\](.*?)(?=\[|$)', research, re.DOTALL | re.IGNORECASE)
        if hist_match:
            parsed["historical"] = hist_match.group(1).strip()
        
        # Extract synthesis/combined section
        synth_match = re.search(r'\[SYNTHESIS.*?\](.*?)(?=\[|$)', research, re.DOTALL | re.IGNORECASE)
        if synth_match:
            parsed["synthesis"] = synth_match.group(1).strip()
        
        return parsed
    
    def _extract_patterns(self, parsed_research: Dict[str, str], query: str) -> List[str]:
        """Extract key patterns and trends from research data.
        
        Args:
            parsed_research: Parsed research data sections
            query: Original query for context
        
        Returns:
            List of identified patterns
        """
        patterns = []
        combined_text = " ".join([
            parsed_research.get("real_time", ""),
            parsed_research.get("historical", ""),
            parsed_research.get("synthesis", "")
        ]).lower()
        
        # Pattern extraction keywords
        pattern_keywords = {
            "growth": r'(grow|increas|rise|surge|expand|accelerat)',
            "decline": r'(declin|decreas|fall|drop|shrink|contract)',
            "stability": r'(stabil|constant|maintain|consistent|flat)',
            "volatility": r'(volatil|fluctuat|swing|unstable|erratic)',
            "trend": r'(trend|movement|direction|shift|transition)',
            "cycle": r'(cycl|period|phase|season|pattern)',
            "correlation": r'(correlat|relat|link|connect|associat)',
            "anomaly": r'(anomal|abnormal|unusual|outlier|exception)'
        }
        
        # Find patterns
        for pattern_type, regex in pattern_keywords.items():
            if re.search(regex, combined_text):
                patterns.append(f"{pattern_type.capitalize()} identified in data")
        
        # If no patterns found, provide general analysis
        if not patterns:
            patterns = [
                "Consistent data presence across sources",
                "Multi-source information synthesis"
            ]
        
        logger.info(f"Extracted {len(patterns)} patterns")
        return patterns
    
    def _calculate_statistics(self, parsed_research: Dict[str, str], patterns: List[str]) -> Dict[str, Any]:
        """Calculate statistics and metrics from research data.
        
        Args:
            parsed_research: Parsed research sections
            patterns: Identified patterns
        
        Returns:
            Dictionary with calculated statistics
        """
        text = " ".join([
            parsed_research.get("real_time", ""),
            parsed_research.get("historical", ""),
            parsed_research.get("synthesis", "")
        ])
        
        statistics = {
            "total_characters": len(text),
            "total_words": len(text.split()),
            "total_sentences": len(re.split(r'[.!?]+', text)),
            "patterns_count": len(patterns),
            "data_sources": len([s for s in parsed_research.values() if s]),
            "real_time_content": "present" if parsed_research.get("real_time") else "absent",
            "historical_content": "present" if parsed_research.get("historical") else "absent"
        }
        
        # Calculate coverage metrics
        total_sections = sum(1 for v in parsed_research.values() if v)
        statistics["data_coverage_percentage"] = (total_sections / 3) * 100
        
        logger.info(f"Calculated {len(statistics)} statistics")
        return statistics
    
    def _generate_insights(
        self,
        query: str,
        plan: str,
        parsed_research: Dict[str, str],
        patterns: List[str],
        statistics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate insights using LLM analysis.
        
        Args:
            query: Original user query
            plan: Planner's plan
            parsed_research: Parsed research data
            patterns: Extracted patterns
            statistics: Calculated statistics
        
        Returns:
            Dictionary with insights and confidence level
        """
        # Build analysis prompt
        prompt = f"""You are a Data Analysis Expert. Analyze the following research findings and extract key insights.

ORIGINAL QUERY: {query}

RESEARCH SUMMARY:
- Real-time data: {'Present' if parsed_research.get('real_time') else 'Absent'}
- Historical data: {'Present' if parsed_research.get('historical') else 'Absent'}
- Patterns identified: {', '.join(patterns[:5])}
- Total words analyzed: {statistics.get('total_words', 0)}

RESEARCH CONTENT:
{parsed_research.get('synthesis', parsed_research.get('real_time', parsed_research.get('historical', 'N/A')))}

Your tasks:
1. Extract 3-5 KEY INSIGHTS that directly answer the original query
2. For each insight, provide a one-sentence explanation
3. Rate overall CONFIDENCE LEVEL (0.0-1.0) based on data completeness
4. Identify any DATA GAPS or limitations
5. Suggest what additional information would improve the analysis

Format your response as JSON with these fields:
{{
    "insights": ["insight1", "insight2", "insight3"],
    "insight_explanations": ["explanation1", "explanation2", "explanation3"],
    "confidence_level": 0.85,
    "data_gaps": ["gap1", "gap2"],
    "improvement_suggestions": ["suggestion1", "suggestion2"]
}}

IMPORTANT: Return ONLY valid JSON, no additional text."""
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Parse JSON response
            insights_dict = self._parse_json_response(content)
            
            logger.info(f"Insights generated via LLM, confidence: {insights_dict.get('confidence_level', 0)}")
            return insights_dict
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            # Provide default insights
            return {
                "insights": [
                    "Research data collected from multiple sources",
                    f"Patterns identified: {', '.join(patterns[:3])}",
                    "Analysis complete with available data"
                ],
                "confidence_level": 0.6,
                "data_gaps": ["LLM insight generation failed"],
                "improvement_suggestions": ["Retry insight generation"]
            }
    
    def _assess_data_quality(
        self,
        parsed_research: Dict[str, str],
        patterns: List[str],
        statistics: Dict[str, Any],
        data_classification: str = "COMBINED"
    ) -> Dict[str, Any]:
        """Assess the quality and completeness of research data (QUERY-AWARE).
        
        Now considers the data classification to fairly assess coverage:
        - REAL_TIME: Expects 1 source (real-time only)
        - HISTORICAL: Expects 2 sources (historical + context)
        - COMBINED: Expects all 3 sources (complete coverage)
        
        Args:
            parsed_research: Parsed research sections
            patterns: Identified patterns
            statistics: Calculated statistics
            data_classification: Type of data needed (REAL_TIME, HISTORICAL, COMBINED)
        
        Returns:
            Dictionary with quality assessment
        """
        # Assess coverage (now query-aware)
        actual_coverage = statistics.get("data_coverage_percentage", 0)
        
        # Determine expected coverage based on query classification
        if data_classification == "REAL_TIME":
            expected_coverage = 33.3  # Only real-time data needed (1/3)
            logger.info(f"REAL_TIME query: expecting {expected_coverage}% coverage")
        elif data_classification == "HISTORICAL":
            expected_coverage = 66.6  # Historical + context (2/3)
            logger.info(f"HISTORICAL query: expecting {expected_coverage}% coverage")
        else:  # COMBINED
            expected_coverage = 100.0  # All data types (3/3)
            logger.info(f"COMBINED query: expecting {expected_coverage}% coverage")
        
        # Fair coverage score: compare actual vs expected
        coverage_score = min(1.0, actual_coverage / max(expected_coverage, 1))
        
        # Assess completeness
        has_real_time = bool(parsed_research.get("real_time"))
        has_historical = bool(parsed_research.get("historical"))
        completeness_score = (int(has_real_time) + int(has_historical)) / 2
        
        # Assess consistency (detected patterns)
        consistency_score = len(patterns) / 10  # normalized
        
        # Overall quality score (0-1) - weighted by data type
        overall_score = (coverage_score * 0.5 + completeness_score * 0.3 + consistency_score * 0.2)
        
        # Determine quality level
        if overall_score >= 0.8:
            quality_level = "high"
        elif overall_score >= 0.5:
            quality_level = "medium"
        else:
            quality_level = "low"
        
        assessment = {
            "quality_level": quality_level,
            "quality_score": round(overall_score, 2),
            "details": {
                "data_classification": data_classification,
                "actual_coverage": round(actual_coverage, 1),
                "expected_coverage": round(expected_coverage, 1),
                "coverage_score": round(coverage_score * 100, 1),
                "completeness": round(completeness_score * 100, 1),
                "consistency": round(consistency_score * 100, 1),
                "real_time_available": has_real_time,
                "historical_available": has_historical
            }
        }
        
        logger.info(f"Data quality: {quality_level} (score: {overall_score:.2f})")
        return assessment
    
    def _generate_recommendations(
        self,
        insights: List[str],
        patterns: List[str],
        data_quality: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations based on analysis.
        
        Args:
            insights: Generated insights
            patterns: Identified patterns
            data_quality: Quality assessment
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Base recommendations on insights
        for i, insight in enumerate(insights[:3]):
            if i == 0 and len(insights) > 0:
                recommendations.append(f"Prioritize: {insight}")
            elif i == 1:
                recommendations.append(f"Consider: {insight}")
        
        # Add quality-based recommendations
        if data_quality["quality_level"] == "low":
            recommendations.append("Collect more comprehensive data for better accuracy")
        elif data_quality["quality_level"] == "medium":
            recommendations.append("Supplement analysis with additional data sources")
        
        # Add pattern-based recommendations
        if any("growth" in p.lower() for p in patterns):
            recommendations.append("Leverage identified growth trends for strategy")
        
        if any("decline" in p.lower() for p in patterns):
            recommendations.append("Monitor and mitigate declining trends")
        
        # Ensure at least 3 recommendations
        if len(recommendations) < 3:
            recommendations.extend([
                "Continue monitoring identified patterns",
                "Document findings for future reference",
                "Plan follow-up analysis as new data becomes available"
            ])
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM JSON response safely.
        
        Args:
            response: LLM response text
        
        Returns:
            Parsed dictionary
        """
        try:
            # Try to find JSON in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # Fallback structure
        return {
            "insights": [response[:200]] if response else ["Analysis complete"],
            "confidence_level": 0.5,
            "data_gaps": [],
            "improvement_suggestions": []
        }
    
    def _create_summary(
        self,
        patterns: List[str],
        insights: Dict[str, Any],
        recommendations: List[str]
    ) -> str:
        """Create a human-readable summary of the analysis.
        
        Args:
            patterns: Identified patterns
            insights: Generated insights
            recommendations: Recommendations
        
        Returns:
            Summary text
        """
        summary = f"""
ANALYSIS SUMMARY
================

Key Patterns ({len(patterns)} identified):
{chr(10).join(['- ' + p for p in patterns[:3]])}

Main Insights ({len(insights.get('insights', []))} identified):
{chr(10).join(['- ' + i for i in insights.get('insights', [])[:3]])}

Top Recommendations ({len(recommendations)} suggested):
{chr(10).join(['- ' + r for r in recommendations[:3]])}

Confidence Level: {insights.get('confidence_level', 0):.0%}
"""
        return summary.strip()
