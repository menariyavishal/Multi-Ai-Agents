import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.writer import Writer

w = Writer()
state = {
    "query": "give me a fantastic project idea since i'm in my final year of btech. cse and my placement sessions are going on so i want to build a project that crazily stands out!",
    "plan": "Design a high impact system",
    "research": "AI campus platform",
    "analysis": {"insights": ["Build an AI campus assistant"]},
    "iteration": 1,
    "messages": []
}

try:
    res = w.call(state)
    print("--- WRITER DRAFT RESULT ---")
    print(res.get("draft")[:1000])
except Exception as e:
    import traceback
    print("EXCEPT:")
    traceback.print_exc()
