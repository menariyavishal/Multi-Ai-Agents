import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.workflow_manager import get_workflow_manager

manager = get_workflow_manager()
res = manager.process_query(
    query="give me a fantastic project idea since i'm in my final year of btech. cse and my placement sessions are going on so i want to build a project that crazily stands out!",
    user_id="dalia",
    max_iterations=1
)

print("RAW RESULT KEYS:", list(res.keys()))
print("final_answer value:", repr(res.get("final_answer")))
print("draft value len:", len(res.get("draft", "")))
print("writer_complete:", res.get("writer_complete"))
