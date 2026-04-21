"""Reviewer Agent - Final Quality Gate for polished content."""

import json
import re
from typing import Any, Dict, List, Tuple
from app.agents.base import BaseAgent
from app.core.logger import get_logger

logger = get_logger(__name__)


class Reviewer(BaseAgent):
    """Reviewer agent that validates and gates content quality before delivery."""
    
    def __init__(self):
        """Initialize Reviewer agent with Groq llama-3.3-70b-versatile LLM (temp=0.0)."""
        super().__init__(agent_role="reviewer")
    
    def call(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Review and validate the draft report for quality and completeness.
        
        Args:
            state: Workflow state containing:
                - query: The user's original query
                - draft: The Writer's polished draft
                - analysis: The Analyst's findings
                - plan: The Planner's plan
                - research: The Researcher's findings
                - iteration: Current iteration number
                - messages: Message history
        
        Returns:
            Updated state with:
                - review_feedback: Quality assessment and feedback
                - final_answer: Approved report ready for delivery
                - reviewer_complete: True
                - messages: Updated with review summary
        """
        query = state.get("query", "")
        draft = state.get("draft", "")
        analysis = state.get("analysis", {})
        plan = state.get("plan", "")
        research = state.get("research", "")
        iteration = state.get("iteration", 1)
        messages = state.get("messages", [])
        
        if not draft:
            logger.warning("No draft provided to Reviewer")
            return {
                **state,
                "review_feedback": {
                    "quality_score": 0.0,
                    "quality_level": "Poor",
                    "issues": ["No draft content to review"],
                    "recommendation": "NEEDS_REVISION"
                },
                "final_answer": "",
                "reviewer_complete": True,
                "messages": messages
            }
        
        logger.info(f"Reviewer validating draft (iteration {iteration})")
        
        try:
            # Step 1: Validate structure
            structure_issues = self._validate_structure(draft)
            logger.info(f"Structure validation: {len(structure_issues)} issues found")
            
            # Step 2: Assess content quality
            content_quality = self._assess_content_quality(draft, query)
            logger.info(f"Content quality: {content_quality['rating']}")
            
            # Step 3: Verify data integrity
            integrity_issues = self._verify_data_integrity(draft, analysis)
            logger.info(f"Data integrity: {len(integrity_issues)} issues found")
            
            # Step 4: Check completeness
            completeness_issues = self._check_completeness(draft, query, analysis)
            logger.info(f"Completeness check: {len(completeness_issues)} issues found")
            
            # Step 5: Perform LLM-based quality review
            llm_review = self._perform_llm_review(query, draft, plan, analysis)
            logger.info(f"LLM review complete: {llm_review['rating']}")
            
            # Step 6: Calculate overall quality score
            all_issues = structure_issues + integrity_issues + completeness_issues + llm_review.get("issues", [])
            quality_score = self._calculate_quality_score(all_issues, content_quality, llm_review)
            logger.info(f"Quality score: {quality_score:.2f}")
            
            # Step 7: Generate feedback
            feedback = self._generate_feedback(
                structure_issues,
                content_quality,
                integrity_issues,
                completeness_issues,
                llm_review,
                quality_score
            )
            logger.info(f"Generated {len(feedback['feedback_items'])} feedback items")
            
            # Step 8: Make routing decision
            recommendation = self._make_routing_decision(quality_score, all_issues)
            logger.info(f"Routing decision: {recommendation}")
            
            # Compile review results
            review_feedback = {
                "quality_score": quality_score,
                "quality_level": self._score_to_level(quality_score),
                "structure_valid": len(structure_issues) == 0,
                "content_quality_rating": content_quality["rating"],
                "data_integrity_verified": len(integrity_issues) == 0,
                "completeness_verified": len(completeness_issues) == 0,
                "total_issues": len(all_issues),
                "issues": all_issues,
                "feedback": feedback,
                "recommendation": recommendation,
                "details": {
                    "structure_issues": len(structure_issues),
                    "content_issues": len(content_quality.get("issues", [])),
                    "integrity_issues": len(integrity_issues),
                    "completeness_issues": len(completeness_issues),
                    "llm_review_issues": len(llm_review.get("issues", []))
                }
            }
            
            # Determine final answer based on recommendation
            final_answer = draft if recommendation == "PASS" else ""
            
            return {
                **state,
                "review_feedback": review_feedback,
                "final_answer": final_answer,
                "reviewer_complete": True,
                "messages": messages + [
                    {
                        "role": "assistant",
                        "content": f"Review: Quality {review_feedback['quality_level']} ({quality_score:.0%}), Recommendation: {recommendation}"
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in Reviewer: {str(e)}")
            return {
                **state,
                "review_feedback": {
                    "quality_score": 0.0,
                    "quality_level": "Error",
                    "error": str(e),
                    "recommendation": "NEEDS_REVISION"
                },
                "final_answer": "",
                "reviewer_complete": True,
                "messages": messages
            }
    
    def _validate_structure(self, draft: str) -> List[str]:
        """Validate report structure and sections.
        
        Args:
            draft: The report draft
        
        Returns:
            List of structure issues
        """
        issues = []
        
        # Check for required sections
        required_sections = [
            ("# Comprehensive Analysis Report", "Main title"),
            ("## Executive Summary", "Executive Summary"),
            ("## Key Findings Overview", "Key Findings"),
            ("## Recommendations", "Recommendations"),
            ("## Conclusion", "Conclusion")
        ]
        
        for marker, name in required_sections:
            if marker not in draft:
                issues.append(f"Missing required section: {name}")
        
        # Check for markdown formatting
        lines = draft.split('\n')
        
        # Check title formatting
        if not any(line.startswith('#') for line in lines):
            issues.append("No markdown headers found - structure may be missing")
        
        # Check paragraph structure
        paragraphs = [p.strip() for p in draft.split('\n\n') if p.strip()]
        if len(paragraphs) < 5:
            issues.append("Report appears too short - may lack sufficient content")
        
        # Check for tables (Key Findings Overview)
        if "| Metric | Value |" not in draft:
            issues.append("Missing formatted findings table")
        
        logger.info(f"Structure validation found {len(issues)} issues")
        return issues
    
    def _assess_content_quality(self, draft: str, query: str) -> Dict[str, Any]:
        """Assess overall content quality and readability.
        
        Args:
            draft: The report draft
            query: Original query for context
        
        Returns:
            Quality assessment dictionary
        """
        issues = []
        
        # Check word count
        word_count = len(draft.split())
        if word_count < 300:
            issues.append("Report is too short (< 300 words) - may lack depth")
        elif word_count > 5000:
            issues.append("Report is too long (> 5000 words) - may be too verbose")
        
        # Check sentence structure
        sentences = re.split(r'[.!?]+', draft)
        avg_sentence_length = word_count / max(len(sentences), 1)
        if avg_sentence_length > 30:
            issues.append("Sentences are very long - readability may suffer")
        elif avg_sentence_length < 8:
            issues.append("Sentences are very short - may lack substance")
        
        # Check for query mention
        if query.lower() not in draft.lower():
            issues.append("Original query not directly addressed in report")
        
        # Check for professional language
        unprofessional = ["like", "kinda", "gonna", "dunno", "yeah", "nope"]
        if any(word in draft.lower().split() for word in unprofessional):
            issues.append("Unprofessional language detected")
        
        # Determine rating
        if len(issues) == 0:
            rating = "Excellent"
        elif len(issues) == 1:
            rating = "Good"
        elif len(issues) <= 2:
            rating = "Fair"
        else:
            rating = "Poor"
        
        return {
            "rating": rating,
            "word_count": word_count,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "issues": issues
        }
    
    def _verify_data_integrity(self, draft: str, analysis: Dict[str, Any]) -> List[str]:
        """Verify that analysis data is accurately represented in draft.
        
        Args:
            draft: The report draft
            analysis: The analyst's findings
        
        Returns:
            List of integrity issues
        """
        issues = []
        
        # Check if key metrics are cited
        confidence = analysis.get("confidence_level", 0)
        if f"{confidence:.0%}" not in draft:
            issues.append("Confidence level not cited in report")
        
        data_quality = analysis.get("data_quality", "").upper()
        if data_quality and data_quality not in draft.upper():
            issues.append("Data quality assessment not cited in report")
        
        # Check if recommendations are referenced
        recommendations = analysis.get("recommendations", [])
        if recommendations and "Recommendations" in draft:
            rec_section = draft.split("## Recommendations")[1] if "## Recommendations" in draft else ""
            cited_recs = sum(1 for rec in recommendations[:3] if any(word in rec_section for word in rec.split()[:3]))
            if cited_recs < len(recommendations[:3]):
                issues.append("Not all recommendations are properly cited in report")
        
        # Check if patterns are mentioned
        patterns = analysis.get("patterns", [])
        if patterns:
            pattern_count = sum(1 for p in patterns if any(word in draft.lower() for word in p.lower().split()))
            if pattern_count == 0:
                issues.append("Identified patterns not discussed in report")
        
        # Check if insights are synthesized
        insights = analysis.get("insights", [])
        if insights:
            insight_keywords = set()
            for insight in insights[:2]:
                words = insight.split()[:2]  # First 2 words of each insight
                insight_keywords.update(words)
            
            if not any(word in draft for word in insight_keywords):
                issues.append("Key insights not adequately synthesized in report")
        
        logger.info(f"Data integrity check found {len(issues)} issues")
        return issues
    
    def _check_completeness(
        self,
        draft: str,
        query: str,
        analysis: Dict[str, Any]
    ) -> List[str]:
        """Check if report comprehensively addresses the original query.
        
        Args:
            draft: The report draft
            query: Original query
            analysis: The analyst's findings
        
        Returns:
            List of completeness issues
        """
        issues = []
        
        # Analyze query to extract key topics
        query_words = set(query.lower().split())
        stopwords = {'the', 'is', 'are', 'and', 'or', 'a', 'an', 'in', 'to', 'of'}
        query_words -= stopwords
        
        # Check if key query words are in draft
        draft_lower = draft.lower()
        covered_words = sum(1 for word in query_words if word in draft_lower)
        coverage_ratio = covered_words / max(len(query_words), 1)
        
        if coverage_ratio < 0.5:
            issues.append(f"Query coverage incomplete - only {coverage_ratio:.0%} of key terms addressed")
        
        # Check for conclusions
        if "## Conclusion" not in draft:
            issues.append("No formal conclusion section - findings may not be contextualized")
        
        # Check for recommendations
        if "## Recommendations" not in draft:
            issues.append("No recommendations section - actionability limited")
        
        # Check for forward-looking statements
        forward_words = ["next", "future", "future", "recommend", "suggest", "should"]
        if not any(word in draft.lower() for word in forward_words):
            issues.append("Report lacks forward-looking recommendations")
        
        # Check for sufficient analysis depth
        analysis_depth = len([s for s in draft.split('. ') if len(s.split()) > 15])
        if analysis_depth < 3:
            issues.append("Analysis depth appears insufficient - may lack detailed reasoning")
        
        logger.info(f"Completeness check found {len(issues)} issues")
        return issues
    
    def _perform_llm_review(
        self,
        query: str,
        draft: str,
        plan: str,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform LLM-based quality review (deterministic with temp=0.0).
        
        Args:
            query: Original query
            draft: Report draft
            plan: Planner's plan
            analysis: Analysis findings
        
        Returns:
            LLM review results
        """
        prompt = f"""You are a Professional Report Reviewer. Perform a strict quality review of the following report.

ORIGINAL QUERY: {query}

REPORT TO REVIEW:
{draft[:2000]}...

YOUR REVIEW TASKS (STRICT EVALUATION):
1. Does the report directly and thoroughly answer the original query?
2. Are the recommendations actionable and well-supported by findings?
3. Is the writing clear, professional, and free of errors?
4. Are there any logical inconsistencies or unsupported claims?
5. Is the report well-structured and easy to navigate?
6. Are all key findings and metrics properly cited?

Provide a JSON response with:
{{
    "rating": "Excellent|Good|Fair|Poor",
    "query_addressed": true/false,
    "recommendations_quality": "Strong|Adequate|Weak",
    "writing_quality": "Professional|Acceptable|Poor",
    "logical_consistency": "Consistent|Minor Issues|Significant Issues",
    "structure_quality": "Excellent|Good|Fair|Poor",
    "citation_accuracy": "Accurate|Minor Issues|Significant Issues",
    "critical_issues": ["issue1", "issue2"],
    "strengths": ["strength1", "strength2"],
    "overall_assessment": "Brief 1-2 sentence assessment"
}}

IMPORTANT: Return ONLY valid JSON, no additional text."""
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Parse JSON response
            review_dict = self._parse_json_response(content)
            
            # Convert to issues list
            issues = review_dict.get("critical_issues", [])
            
            logger.info(f"LLM review complete: {review_dict.get('rating', 'Unknown')}")
            return {
                "rating": review_dict.get("rating", "Unknown"),
                "assessment": review_dict.get("overall_assessment", ""),
                "issues": issues,
                "strengths": review_dict.get("strengths", []),
                "details": review_dict
            }
            
        except Exception as e:
            logger.error(f"LLM review failed: {str(e)}")
            return {
                "rating": "Unknown",
                "assessment": "LLM review could not be completed",
                "issues": ["LLM review failed"],
                "strengths": [],
                "details": {}
            }
    
    def _calculate_quality_score(
        self,
        issues: List[str],
        content_quality: Dict[str, Any],
        llm_review: Dict[str, Any]
    ) -> float:
        """Calculate overall quality score (0.0 - 1.0).
        
        Args:
            issues: All identified issues
            content_quality: Content quality assessment
            llm_review: LLM review results
        
        Returns:
            Quality score
        """
        # Start with base score
        score = 1.0
        
        # Deduct for issues (0.05 per issue, capped at 0.5)
        issue_deduction = min(len(issues) * 0.05, 0.5)
        score -= issue_deduction
        
        # Apply content quality multiplier
        quality_multipliers = {
            "Excellent": 1.0,
            "Good": 0.95,
            "Fair": 0.85,
            "Poor": 0.70
        }
        quality_multiplier = quality_multipliers.get(content_quality.get("rating", "Fair"), 0.85)
        score *= quality_multiplier
        
        # Apply LLM review assessment
        llm_multipliers = {
            "Excellent": 1.0,
            "Good": 0.95,
            "Fair": 0.85,
            "Poor": 0.70,
            "Unknown": 0.80
        }
        llm_multiplier = llm_multipliers.get(llm_review.get("rating", "Unknown"), 0.80)
        score *= llm_multiplier
        
        # Ensure score is in valid range
        return max(0.0, min(1.0, score))
    
    def _score_to_level(self, score: float) -> str:
        """Convert score to quality level.
        
        Args:
            score: Quality score (0.0 - 1.0)
        
        Returns:
            Quality level string
        """
        if score >= 0.90:
            return "Excellent"
        elif score >= 0.80:
            return "Good"
        elif score >= 0.70:
            return "Fair"
        elif score >= 0.50:
            return "Poor"
        else:
            return "Critical"
    
    def _generate_feedback(
        self,
        structure_issues: List[str],
        content_quality: Dict[str, Any],
        integrity_issues: List[str],
        completeness_issues: List[str],
        llm_review: Dict[str, Any],
        quality_score: float
    ) -> Dict[str, Any]:
        """Generate comprehensive feedback for the report.
        
        Args:
            structure_issues: Structure validation issues
            content_quality: Content quality assessment
            integrity_issues: Data integrity issues
            completeness_issues: Completeness issues
            llm_review: LLM review results
            quality_score: Overall quality score
        
        Returns:
            Feedback dictionary
        """
        feedback_items = []
        
        # Add positive feedback from strengths
        for strength in llm_review.get("strengths", []):
            feedback_items.append({
                "type": "strength",
                "message": f"✅ {strength}"
            })
        
        # Add structural issues
        for issue in structure_issues:
            feedback_items.append({
                "type": "structure",
                "message": f"⚠️ {issue}"
            })
        
        # Add content quality issues
        for issue in content_quality.get("issues", []):
            feedback_items.append({
                "type": "content",
                "message": f"⚠️ {issue}"
            })
        
        # Add integrity issues
        for issue in integrity_issues:
            feedback_items.append({
                "type": "integrity",
                "message": f"❌ {issue}"
            })
        
        # Add completeness issues
        for issue in completeness_issues:
            feedback_items.append({
                "type": "completeness",
                "message": f"⚠️ {issue}"
            })
        
        # Add LLM review issues
        for issue in llm_review.get("issues", []):
            feedback_items.append({
                "type": "llm_review",
                "message": f"❌ {issue}"
            })
        
        return {
            "summary": llm_review.get("assessment", ""),
            "feedback_items": feedback_items,
            "quality_score": quality_score,
            "item_count": len(feedback_items)
        }
    
    def _make_routing_decision(self, quality_score: float, issues: List[str]) -> str:
        """Make routing decision: PASS or NEEDS_REVISION.
        
        Args:
            quality_score: Overall quality score
            issues: All identified issues
        
        Returns:
            Routing decision
        """
        # Strict thresholds for final gate
        if quality_score >= 0.80 and len(issues) <= 3:
            return "PASS"
        else:
            return "NEEDS_REVISION"
    
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
            "rating": "Unknown",
            "critical_issues": [],
            "strengths": [],
            "overall_assessment": "Unable to parse review"
        }
