"""Integration test: Chain all 5 agents together - Planner → Researcher → Analyst → Writer → Reviewer."""

import json
from app.agents.planner import Planner
from app.agents.researcher import Researcher
from app.agents.analyst import Analyst
from app.agents.writer import Writer
from app.agents.reviewer import Reviewer
from app.core.logger import get_logger

logger = get_logger(__name__)


def test_five_agent_workflow():
    """Test complete workflow: Planner → Researcher → Analyst."""
    
    print("\n" + "="*80)
    print("MULTI-AGENT WORKFLOW TEST: Planner → Researcher → Analyst → Writer → Reviewer")
    print("="*80)
    
    # Initialize agents
    print("\n[1] Initializing agents...")
    planner = Planner()
    researcher = Researcher()
    analyst = Analyst()
    writer = Writer()
    reviewer = Reviewer()
    print("    ✅ Planner initialized")
    print("    ✅ Researcher initialized")
    print("    ✅ Analyst initialized")
    print("    ✅ Writer initialized")
    print("    ✅ Reviewer initialized")
    
    # Step 1: Planner - Create plan from query
    print("\n" + "-"*80)
    print("[2] PLANNER AGENT - Creating execution plan")
    print("-"*80)
    
    query = "What are the current trends in AI and machine learning?"
    print(f"📝 Query: {query}")
    
    initial_state = {
        "query": query,
        "messages": []
    }
    
    print("\n⏳ Planner processing...")
    planner_result = planner.call(initial_state)
    
    plan = planner_result.get("plan", "")
    print(f"\n✅ Plan generated ({len(plan)} characters)")
    print("\n📋 Plan:")
    print("-" * 80)
    print(plan[:500] + ("..." if len(plan) > 500 else ""))
    print("-" * 80)
    
    # Step 2: Researcher - Gather data based on plan
    print("\n" + "-"*80)
    print("[3] RESEARCHER AGENT - Gathering data based on plan")
    print("-"*80)
    
    researcher_state = {
        **planner_result,
        "query": query,
        "plan": plan
    }
    
    print("\n⏳ Researcher processing...")
    researcher_result = researcher.call(researcher_state)
    
    research = researcher_result.get("research", "")
    print(f"\n✅ Research gathered ({len(research)} characters)")
    print("\n📊 Research Summary:")
    print("-" * 80)
    print(research[:600] + ("..." if len(research) > 600 else ""))
    print("-" * 80)
    
    # Step 3: Analyst - Extract patterns and insights
    print("\n" + "-"*80)
    print("[4] ANALYST AGENT - Analyzing research findings")
    print("-"*80)
    
    analyst_state = {
        **researcher_result,
        "query": query,
        "plan": plan,
        "research": research
    }
    
    print("\n⏳ Analyst processing...")
    analyst_result = analyst.call(analyst_state)
    
    analysis = analyst_result.get("analysis", {})
    print(f"\n✅ Analysis complete")
    
    # Step 4: Writer - Synthesize analysis into polished content
    print("\n" + "-"*80)
    print("[5] WRITER AGENT - Synthesizing into polished content")
    print("-"*80)
    
    writer_state = {
        **analyst_result,
        "query": query,
        "plan": plan,
        "research": research,
        "analysis": analysis
    }
    
    print("\n⏳ Writer processing...")
    writer_result = writer.call(writer_state)
    
    draft = writer_result.get("draft", "")
    print(f"\n✅ Draft created ({len(draft)} characters, {len(draft.split())} words)")
    print("\n📄 Draft Preview:")
    print("-" * 80)
    print(draft[:800] + ("..." if len(draft) > 800 else ""))
    print("-" * 80)
    
    # Step 5: Reviewer - Final quality gate
    print("\n" + "-"*80)
    print("[6] REVIEWER AGENT - Final Quality Gate")
    print("-"*80)
    
    reviewer_state = {
        **writer_result,
        "query": query,
        "plan": plan,
        "research": research,
        "analysis": analysis,
        "draft": draft
    }
    
    print("\n⏳ Reviewer processing...")
    reviewer_result = reviewer.call(reviewer_state)
    
    review_feedback = reviewer_result.get("review_feedback", {})
    final_answer = reviewer_result.get("final_answer", "")
    
    print(f"\n✅ Review complete")
    print(f"   Quality Score: {review_feedback.get('quality_score', 0):.0%}")
    print(f"   Quality Level: {review_feedback.get('quality_level', 'Unknown')}")
    print(f"   Recommendation: {review_feedback.get('recommendation', 'Unknown')}")
    print(f"   Total Issues Found: {review_feedback.get('total_issues', 0)}")
    print(f"   Final Answer Status: {'✅ APPROVED' if final_answer else '❌ NEEDS_REVISION'}")
    
    # Print Final Report
    print("\n" + "="*80)
    print("FINAL APPROVED REPORT (if passed review)")
    print("="*80)
    if final_answer:
        print(final_answer[:1200] + ("..." if len(final_answer) > 1200 else ""))
    else:
        print("⚠️ Report did not pass review - see feedback below")
    
    # Review Feedback Summary
    print("\n" + "="*80)
    print("REVIEW FEEDBACK")
    print("="*80)
    
    feedback = review_feedback.get("feedback", {})
    print(f"\n📝 Review Summary: {feedback.get('summary', 'N/A')}")
    print(f"\n📊 Review Details:")
    print(f"   • Structure Valid: {'✅ Yes' if review_feedback.get('structure_valid') else '❌ No'}")
    print(f"   • Content Quality: {review_feedback.get('content_quality_rating', 'Unknown')}")
    print(f"   • Data Integrity: {'✅ Verified' if review_feedback.get('data_integrity_verified') else '❌ Issues Found'}")
    print(f"   • Completeness: {'✅ Complete' if review_feedback.get('completeness_verified') else '❌ Incomplete'}")
    
    print(f"\n🔍 Issue Breakdown:")
    details = review_feedback.get("details", {})
    print(f"   • Structure Issues: {details.get('structure_issues', 0)}")
    print(f"   • Content Issues: {details.get('content_issues', 0)}")
    print(f"   • Integrity Issues: {details.get('integrity_issues', 0)}")
    print(f"   • Completeness Issues: {details.get('completeness_issues', 0)}")
    print(f"   • LLM Review Issues: {details.get('llm_review_issues', 0)}")
    
    if feedback.get("feedback_items"):
        print(f"\n💬 Feedback Items ({len(feedback['feedback_items'])} total):")
        for item in feedback['feedback_items'][:5]:
            print(f"   {item['message']}")
        if len(feedback['feedback_items']) > 5:
            print(f"   ... and {len(feedback['feedback_items']) - 5} more items")
    
    # Print Final Analysis Results
    print("\n" + "="*80)
    print("FINAL ANALYSIS RESULTS (Summary)")
    print("="*80)
    
    print(f"\n🎯 Status: {analysis.get('status', 'unknown').upper()}")
    print(f"📊 Data Quality: {analysis.get('data_quality', 'unknown').upper()}")
    print(f"💯 Confidence Level: {analysis.get('confidence_level', 0):.0%}")
    
    # Patterns
    patterns = analysis.get("patterns", [])
    print(f"\n🔍 Patterns Identified ({len(patterns)}):")
    for i, pattern in enumerate(patterns, 1):
        print(f"   {i}. {pattern}")
    
    # Statistics
    statistics = analysis.get("statistics", {})
    print(f"\n📈 Statistics:")
    print(f"   • Total Words: {statistics.get('total_words', 0):,}")
    print(f"   • Total Sentences: {statistics.get('total_sentences', 0)}")
    print(f"   • Data Coverage: {statistics.get('data_coverage_percentage', 0):.1f}%")
    print(f"   • Data Sources: {statistics.get('data_sources', 0)}")
    
    # Insights
    insights = analysis.get("insights", [])
    print(f"\n💡 Key Insights ({len(insights)}):")
    for i, insight in enumerate(insights, 1):
        print(f"   {i}. {insight}")
    
    # Recommendations
    recommendations = analysis.get("recommendations", [])
    print(f"\n✨ Recommendations ({len(recommendations)}):")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    # Data Quality Details
    dq_details = analysis.get("data_quality_details", {})
    if dq_details:
        print(f"\n🏆 Data Quality Details:")
        print(f"   • Coverage: {dq_details.get('coverage', 0):.1f}%")
        print(f"   • Completeness: {dq_details.get('completeness', 0):.1f}%")
        print(f"   • Consistency: {dq_details.get('consistency', 0):.1f}%")
        print(f"   • Real-time Data: {'✅ Available' if dq_details.get('real_time_available') else '❌ Not Available'}")
        print(f"   • Historical Data: {'✅ Available' if dq_details.get('historical_available') else '❌ Not Available'}")
    
    # Analysis Summary
    print("\n" + "="*80)
    print("ANALYSIS SUMMARY")
    print("="*80)
    summary = analysis.get("analysis_summary", "")
    print(summary)
    
    # Final Status
    print("\n" + "="*80)
    print("✅ WORKFLOW COMPLETE")
    print("="*80)
    print(f"\nTotal state keys in final result: {len(reviewer_result)}")
    print(f"Keys: {', '.join(reviewer_result.keys())}")
    
    # Verify all stages completed
    print("\n📋 Stage Completion Status:")
    print(f"   • Planner: {'✅' if planner_result.get('planner_complete') else '❌'}")
    print(f"   • Researcher: {'✅' if researcher_result.get('researcher_complete') else '❌'}")
    print(f"   • Analyst: {'✅' if analyst_result.get('analyst_complete') else '❌'}")
    print(f"   • Writer: {'✅' if writer_result.get('writer_complete') else '❌'}")
    print(f"   • Reviewer: {'✅' if reviewer_result.get('reviewer_complete') else '❌'}")
    
    print("\n📋 Workflow Result:")
    if review_feedback.get('recommendation') == 'PASS':
        print(f"   ✅ REPORT APPROVED - Quality: {review_feedback.get('quality_level')}")
    else:
        print(f"   ⚠️ REPORT NEEDS REVISION - Quality: {review_feedback.get('quality_level')}")
    
    print("\n" + "="*80)
    
    # Verify results
    assert planner_result.get("planner_complete") is True
    assert researcher_result.get("researcher_complete") is True
    assert analyst_result.get("analyst_complete") is True
    assert writer_result.get("writer_complete") is True
    assert reviewer_result.get("reviewer_complete") is True
    assert analysis.get("status") == "success"
    assert len(draft) > 0
    assert review_feedback.get("quality_score", 0) > 0
    
    print("✅ All assertions passed - workflow successful!\n")
    
    return reviewer_result


if __name__ == "__main__":
    test_five_agent_workflow()
