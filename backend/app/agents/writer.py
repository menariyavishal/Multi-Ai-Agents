"""Writer Agent - Synthesizes analysis into polished written content."""

import json
from typing import Any, Dict, List
from app.agents.base import BaseAgent
from app.core.logger import get_logger

logger = get_logger(__name__)


class Writer(BaseAgent):
    """Writer agent that synthesizes research and analysis into polished written content."""
    
    def __init__(self):
        """Initialize Writer agent with Groq llama-3.3-70b-versatile LLM."""
        super().__init__(agent_role="writer")
    
    def call(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Write polished content based on research and analysis.
        
        Args:
            state: Workflow state containing:
                - query: The user's original query
                - plan: The Planner's detailed plan
                - research: The Researcher's gathered findings
                - analysis: The Analyst's findings and insights
                - iteration: Current iteration number
                - messages: Message history
        
        Returns:
            Updated state with:
                - draft: Written content
                - writer_complete: True
                - messages: Updated with writing summary
        """
        query = state.get("query", "")
        plan = state.get("plan", "")
        research = state.get("research", "")
        analysis = state.get("analysis", {})
        iteration = state.get("iteration", 1)
        messages = state.get("messages", [])
        
        if not query:
            logger.warning("No query provided to Writer")
            return {
                **state,
                "draft": "",
                "writer_complete": True,
                "messages": messages
            }
        
        logger.info(f"Writer synthesizing content for query (iteration {iteration})")
        
        try:
            # Step 1: Extract key information from analysis
            insights = self._extract_key_information(analysis)
            logger.info(f"Extracted {len(insights)} key insights for writing")
            
            # Step 2: Create executive summary
            executive_summary = self._create_executive_summary(
                query,
                analysis
            )
            logger.info("Executive summary created")
            
            # Step 3: Write main body with analysis synthesis
            main_body = self._write_main_body(
                query,
                plan,
                research,
                analysis,
                insights
            )
            logger.info(f"Main body written ({len(main_body)} characters)")
            
            # Step 4: Create recommendations section
            recommendations_section = self._write_recommendations(
                analysis.get("recommendations", []),
                analysis.get("insights", [])
            )
            logger.info("Recommendations section created")
            
            # Step 5: Create conclusion
            conclusion = self._write_conclusion(
                query,
                analysis.get("confidence_level", 0),
                analysis.get("data_quality", "unknown")
            )
            logger.info("Conclusion written")
            
            # Step 6: Compile final draft
            draft = self._compile_final_draft(
                query,
                executive_summary,
                main_body,
                recommendations_section,
                conclusion,
                analysis
            )
            logger.info(f"Final draft compiled ({len(draft)} characters)")
            
            return {
                **state,
                "draft": draft,
                "writer_complete": True,
                "messages": messages + [
                    {
                        "role": "assistant",
                        "content": f"Writing: Draft created ({len(draft)} chars, {len(draft.split())} words)"
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in Writer: {str(e)}")
            return {
                **state,
                "draft": "",
                "writer_error": str(e),
                "writer_complete": True,
                "messages": messages
            }
    
    def _extract_key_information(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract key information from analysis for synthesis.
        
        Args:
            analysis: The analyst's findings
        
        Returns:
            List of key information dictionaries
        """
        key_info = []
        
        # Extract patterns as key information
        for pattern in analysis.get("patterns", [])[:3]:
            key_info.append({
                "type": "pattern",
                "content": pattern
            })
        
        # Extract top insights
        for insight in analysis.get("insights", [])[:3]:
            key_info.append({
                "type": "insight",
                "content": insight
            })
        
        # Add confidence level
        confidence = analysis.get("confidence_level", 0)
        key_info.append({
            "type": "confidence",
            "content": f"{confidence:.0%}"
        })
        
        return key_info
    
    def _create_executive_summary(
        self,
        query: str,
        analysis: Dict[str, Any]
    ) -> str:
        """Create an executive summary of the analysis.
        
        Args:
            query: Original user query
            analysis: The analyst's findings
        
        Returns:
            Executive summary text
        """
        confidence = analysis.get("confidence_level", 0)
        data_quality = analysis.get("data_quality", "unknown")
        insights_count = len(analysis.get("insights", []))
        patterns_count = len(analysis.get("patterns", []))
        
        summary = f"""## Executive Summary

This comprehensive analysis addresses: **{query}**

The investigation identified **{patterns_count} key patterns** and **{insights_count} significant insights** based on multi-source research and data synthesis. The analysis confidence level is **{confidence:.0%}**, with data quality assessed as **{data_quality.upper()}**.

This report synthesizes findings into actionable recommendations for decision-making and strategic planning."""
        
        return summary
    
    def _write_main_body(
        self,
        query: str,
        plan: str,
        research: str,
        analysis: Dict[str, Any],
        insights: List[Dict[str, str]]
    ) -> str:
        """Write the main body of the report using LLM.
        
        Args:
            query: Original query
            plan: Planner's plan
            research: Researcher's findings
            analysis: Analyst's findings
            insights: Extracted key insights
        
        Returns:
            Main body text
        """
        # Build prompt for LLM
        patterns_list = "\n".join([f"- {p}" for p in analysis.get("patterns", [])[:5]])
        insights_list = "\n".join([f"- {i}" for i in analysis.get("insights", [])[:5]])
        stats = analysis.get("statistics", {})
        
        prompt = f"""You are a Professional Report Writer. Create a well-structured main body section that synthesizes the following research and analysis findings.

QUERY: {query}

KEY PATTERNS IDENTIFIED:
{patterns_list}

MAIN INSIGHTS:
{insights_list}

RESEARCH STATISTICS:
- Total data analyzed: {stats.get('total_words', 0)} words from {stats.get('data_sources', 0)} sources
- Data coverage: {stats.get('data_coverage_percentage', 0):.1f}%
- Real-time data: Available
- Historical context: Available

TASK:
Write 2-3 comprehensive paragraphs that:
1. Synthesize the patterns and insights into a cohesive narrative
2. Explain the significance of findings
3. Connect findings to the original query
4. Use professional language and clear structure
5. Include specific data points where relevant

Format as markdown with clear paragraph structure. NO HEADERS. Focus on flowing prose that integrates all key findings naturally."""
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            logger.info("Main body generated via LLM")
            return content
        except Exception as e:
            logger.error(f"Error generating main body: {str(e)}")
            # Provide fallback
            fallback = f"""The analysis of "{query}" reveals significant patterns and insights from comprehensive research.

Key findings indicate {len(analysis.get('patterns', []))} distinct patterns across the studied domain. These patterns are supported by {len(analysis.get('insights', []))} major insights derived from both real-time and historical data.

The research demonstrates {analysis.get('data_quality', 'uncertain').lower()} data quality with a confidence level of {analysis.get('confidence_level', 0):.0%}, indicating the reliability of the findings for decision-making purposes."""
            return fallback
    
    def _write_recommendations(
        self,
        recommendations: List[str],
        insights: List[str]
    ) -> str:
        """Create recommendations section.
        
        Args:
            recommendations: List of recommendations from Analyst
            insights: List of insights for context
        
        Returns:
            Formatted recommendations section
        """
        if not recommendations:
            return "## Recommendations\n\nNo specific recommendations available at this time."
        
        section = "## Recommendations\n\n"
        section += "Based on the analysis, the following actionable recommendations are proposed:\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            # Clean up recommendation text
            clean_rec = rec.replace("Prioritize:", "").replace("Consider:", "").strip()
            section += f"{i}. **{clean_rec}**\n"
        
        # Add implementation note
        section += f"\n### Implementation Priority\n\n"
        section += f"These {len(recommendations)} recommendations are prioritized based on their impact potential and feasibility. "
        section += f"Implementation should begin with the highest-impact recommendations first, supported by the insights derived from the data analysis."
        
        return section
    
    def _write_conclusion(
        self,
        query: str,
        confidence: float,
        data_quality: str
    ) -> str:
        """Write conclusion section.
        
        Args:
            query: Original query
            confidence: Confidence level from analysis
            data_quality: Quality assessment
        
        Returns:
            Conclusion text
        """
        quality_assessment = {
            "high": "The analysis is built on robust, comprehensive data with high reliability.",
            "medium": "The analysis is supported by adequate data with moderate reliability.",
            "low": "The analysis would benefit from additional data sources for greater confidence."
        }.get(data_quality.lower(), "The analysis is supported by available data sources.")
        
        confidence_statement = {
            (0.8, 1.0): "The findings are highly reliable and suitable for strategic decision-making.",
            (0.6, 0.8): "The findings are moderately reliable and should be considered alongside other factors.",
            (0.4, 0.6): "The findings suggest trends but should be validated with additional research.",
            (0.0, 0.4): "The findings indicate preliminary patterns that require further investigation."
        }
        
        conf_text = "The findings are highly reliable"
        for (low, high), text in confidence_statement.items():
            if low <= confidence <= high:
                conf_text = text
                break
        
        conclusion = f"""## Conclusion

This analysis of "{query}" provides evidence-based insights derived from comprehensive research and rigorous data analysis.

{quality_assessment} {conf_text}

The identified patterns and insights serve as a foundation for informed decision-making and strategic planning. Organizations should monitor the evolving trends identified in this analysis and continue to gather additional data to validate and refine these findings over time.

Moving forward, maintaining data collection practices and periodic re-analysis will ensure that strategies remain aligned with current market conditions and emerging trends."""
        
        return conclusion
    
    def _compile_final_draft(
        self,
        query: str,
        executive_summary: str,
        main_body: str,
        recommendations: str,
        conclusion: str,
        analysis: Dict[str, Any]
    ) -> str:
        """Compile all sections into final draft.
        
        Args:
            query: Original query
            executive_summary: Summary section
            main_body: Main body section
            recommendations: Recommendations section
            conclusion: Conclusion section
            analysis: Original analysis for metadata
        
        Returns:
            Complete draft document
        """
        # Create document header
        header = f"""# Comprehensive Analysis Report

**Query:** {query}

**Report Generated:** Analysis completed with data quality: {analysis.get('data_quality', 'unknown').upper()}

**Analysis Confidence:** {analysis.get('confidence_level', 0):.0%}

---

"""
        
        # Add metadata section
        metadata = self._create_metadata_section(analysis)
        
        # Compile full document
        full_draft = header + executive_summary + "\n\n" + metadata + "\n\n" + main_body + "\n\n" + recommendations + "\n\n" + conclusion
        
        return full_draft
    
    def _create_metadata_section(self, analysis: Dict[str, Any]) -> str:
        """Create metadata/findings overview section.
        
        Args:
            analysis: Analysis results
        
        Returns:
            Metadata section
        """
        stats = analysis.get("statistics", {})
        
        section = "## Key Findings Overview\n\n"
        section += f"| Metric | Value |\n"
        section += f"|--------|-------|\n"
        section += f"| Patterns Identified | {len(analysis.get('patterns', []))} |\n"
        section += f"| Key Insights | {len(analysis.get('insights', []))} |\n"
        section += f"| Data Coverage | {stats.get('data_coverage_percentage', 0):.1f}% |\n"
        section += f"| Data Sources | {stats.get('data_sources', 0)} |\n"
        section += f"| Confidence Level | {analysis.get('confidence_level', 0):.0%} |\n"
        section += f"| Data Quality | {analysis.get('data_quality', 'Unknown').capitalize()} |\n"
        
        return section
