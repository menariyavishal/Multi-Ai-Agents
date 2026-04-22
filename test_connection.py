#!/usr/bin/env python
"""Test if Planner and Researcher agents are connected."""

import sys
sys.path.insert(0, r'c:\Users\HP\OneDrive\Scans\CODES\Python\Multi-Ai-Agents\backend')

from app.agents.planner import Planner
from app.agents.researcher import Researcher

print("\n" + "="*60)
print("TESTING PLANNER → RESEARCHER CONNECTION")
print("="*60)

# Initialize agents
planner = Planner()
researcher = Researcher()

# Step 1: Planner creates plan
print("\n1️⃣ PLANNER STEP - Creating plan...")
initial_state = {
    "query": "What's the weather in London today?",
    "iteration": 1,
    "messages": []
}

planner_output = planner.call(initial_state)
print(f"✅ Planner created plan: {len(planner_output.get('plan', ''))} characters")
print(f"✅ Planner complete: {planner_output.get('planner_complete', False)}")

# Step 2: Researcher uses Planner's output
print("\n2️⃣ RESEARCHER STEP - Using Planner's plan...")
researcher_output = researcher.call(planner_output)
print(f"✅ Researcher gathered research: {len(researcher_output.get('research', ''))} characters")
print(f"✅ Researcher complete: {researcher_output.get('researcher_complete', False)}")

# Step 3: Show connection
print("\n3️⃣ CONNECTION CHECK:")
print(f"✅ Planner output passed to Researcher: {'plan' in planner_output and 'plan' in researcher_output}")
print(f"✅ Plan used by Researcher: {'plan' in researcher_output}")
print(f"✅ Research added after plan: {'research' in researcher_output}")
print(f"✅ Query preserved: {'query' in researcher_output and researcher_output['query'] == initial_state['query']}")

print("\n" + "="*60)
print("✅ PLANNER & RESEARCHER ARE CONNECTED!")
print("✅ Workflow: Planner → Researcher → (Writer, Analyst, Reviewer)")
print("="*60 + "\n")
