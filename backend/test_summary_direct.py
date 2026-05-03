import sys
import json
sys.path.insert(0, '.')

# Direct test of the method
from app.services.workflow_manager import WorkflowManager

# Create a mock result with insights
mock_result = {
    "query": "test",
    "plan": "test plan",
    "research": "test research",
    "iteration": 1,
    "final_answer": "test answer",
    "draft": "",
    "analysis": {
        "patterns": ["pattern1", "pattern2"],
        "insights": ["insight1", "insight2"],
        "recommendations": ["rec1", "rec2"],
        "confidence_level": 0.85,
        "data_quality": "high"
    },
    "review_feedback": {},
    "planner_complete": True,
    "researcher_complete": True,
    "analyst_complete": True,
    "writer_complete": True,
    "reviewer_complete": True,
    "elapsed_seconds": 10
}

manager = WorkflowManager()
summary = manager.get_result_summary(mock_result)

print("\n=== DIRECT TEST RESULTS ===")
print(f"Summary analysis keys: {list(summary['analysis'].keys())}")
print(f"Has 'insights'? {'insights' in summary['analysis']}")
print(f"Insights value: {summary['analysis'].get('insights', 'NOT FOUND')}")
print(f"Insights type: {type(summary['analysis'].get('insights'))}")

# Try to JSON serialize it
try:
    json_str = json.dumps(summary)
    json_obj = json.loads(json_str)
    print(f"\nAfter JSON roundtrip:")
    print(f"Has 'insights'? {'insights' in json_obj['analysis']}")
    print(f"Insights: {json_obj['analysis'].get('insights', 'NOT FOUND')}")
except Exception as e:
    print(f"JSON error: {e}")
