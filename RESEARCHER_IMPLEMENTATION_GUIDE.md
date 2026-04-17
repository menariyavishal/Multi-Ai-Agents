# How to Implement Researcher Agent - Step by Step

## **Your Task:**
Create `backend/app/agents/researcher.py` that reads Planner's output and decides which data sources to use.

---

## **Step 1: Understand the Pattern**

Look at the **Planner agent** as your template:
```
File: backend/app/agents/planner.py
```

**Key Pattern:**
```python
class Planner(BaseAgent):
    def __init__(self):
        super().__init__(agent_role="planner")
    
    def call(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Extract from state
        query = state.get("query", "")
        
        # 2. Build prompt
        prompt = self._build_planning_prompt(query, ...)
        
        # 3. Call LLM
        response = self.llm.invoke(prompt)
        
        # 4. Return updated state
        return {
            **state,
            "plan": plan,
            "planner_complete": True,
            "messages": [...]
        }
    
    def _build_planning_prompt(self, query, ...):
        # Return prompt string
        pass
```

---

## **Step 2: Create Researcher Structure**

Your `researcher.py` should follow the same pattern:

```python
from typing import Any, Dict
from app.agents.base import BaseAgent
from app.core.logger import get_logger

logger = get_logger(__name__)

class Researcher(BaseAgent):
    def __init__(self):
        # TODO: Call parent with agent_role="researcher"
        pass
    
    def call(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: Get plan from state
        # TODO: Analyze plan to determine data sources
        # TODO: Gather data from selected sources
        # TODO: Return updated state with "research" field
        pass
    
    def _analyze_plan(self, plan: str) -> Dict[str, Any]:
        # TODO: Send plan to LLM asking what data sources needed
        # Should return: {
        #     "data_type": "REAL_TIME" | "HISTORICAL" | "COMBINED",
        #     "sources": ["MCP_SERVERS"] or ["DATABASE"] or both,
        #     "reasoning": "...",
        #     "data_to_gather": "..."
        # }
        pass
    
    def _gather_data(self, sources: list, query: str) -> str:
        # TODO: Mock data gathering from chosen sources
        # If "MCP_SERVERS" in sources: gather real-time data
        # If "DATABASE" in sources: gather historical data
        pass
    
    def _synthesize_research(self, data: str) -> str:
        # TODO: Combine gathered data into comprehensive research
        pass
```

---

## **Step 3: What Data to Read from State**

```python
def call(self, state: Dict[str, Any]) -> Dict[str, Any]:
    # Get these from state:
    query = state.get("query", "")           # User's original query
    plan = state.get("plan", "")             # Planner's plan (THIS IS KEY!)
    iteration = state.get("iteration", 1)
    messages = state.get("messages", [])
```

---

## **Step 4: Analyze Plan with LLM**

Use the pattern from `test_researcher_real_llm.py`:

```python
def _analyze_plan(self, plan: str) -> Dict[str, Any]:
    prompt = f"""You are a Research Agent.
    
PLANNER'S PLAN:
{plan}

Decide:
1. What DATA SOURCES? (MCP_SERVERS for real-time, DATABASE for historical, or BOTH)
2. WHY these sources?
3. What data to gather?

Format:
DATA_SOURCES: [answer]
REASONING: [answer]
DATA_TO_GATHER: [answer]
"""
    response = self.llm.invoke(prompt)
    
    # Parse response and return dict
    # TODO: Extract DATA_SOURCES, REASONING, DATA_TO_GATHER from response
```

---

## **Step 5: Mock Data Gathering**

```python
def _gather_data(self, sources: list, query: str) -> str:
    data_parts = []
    
    if "MCP_SERVERS" in sources:
        # Mock real-time data gathering
        data_parts.append(f"""
[Real-time Data from MCP_SERVERS for: {query}]
- Current market trends
- Latest technologies
- Live data sources
- Up-to-date information
""")
    
    if "DATABASE" in sources:
        # Mock historical data gathering
        data_parts.append(f"""
[Historical Data from DATABASE for: {query}]
- Historical context
- Past patterns
- Proven approaches
- Evolution data
""")
    
    return "\n".join(data_parts)
```

---

## **Step 6: Synthesize Research**

```python
def _synthesize_research(self, data: str, analysis: Dict) -> str:
    synthesis = f"""
RESEARCH SYNTHESIS:

Data Strategy: {analysis['data_type']}

Reasoning: {analysis['reasoning']}

Gathered Data:
{data}

Key Insights:
- {analysis['data_to_gather']}
"""
    return synthesis
```

---

## **Step 7: Return Updated State**

```python
def call(self, state: Dict[str, Any]) -> Dict[str, Any]:
    # ... all the logic ...
    
    return {
        **state,
        "research": research,
        "researcher_complete": True,
        "messages": messages + [
            {"role": "assistant", "content": f"Research: {research[:200]}..."}
        ]
    }
```

---

## **Step 8: Test Your Implementation**

Create `backend/test_researcher_my_implementation.py`:

```python
from app.agents.researcher import Researcher
from app.agents.planner import Planner

# 1. Create Planner and generate plan
planner = Planner()
state = planner.call({
    "query": "Build a mobile app",
    "iteration": 1
})

# 2. Pass plan to Researcher
researcher = Researcher()
result = researcher.call(state)

# 3. Check output
print(f"Plan:\n{result['plan']}\n")
print(f"Research:\n{result['research']}\n")
print(f"Complete: {result['researcher_complete']}")
```

Run it:
```powershell
cd backend
python.exe test_researcher_my_implementation.py
```

---

## **Step 9: Configuration**

Update `backend/app/core/constants.py` to add Researcher config:

```python
MODEL_CONFIGS = {
    "planner": {...},
    "researcher": {  # Add this
        "provider": "groq",
        "name": "llama-3.3-70b-versatile",
        "temperature": 0.2  # More analytical
    },
    # ... other agents ...
}
```

---

## **Checklist Before Implementing Real Agent:**

- [ ] Created `backend/app/agents/researcher.py`
- [ ] Class extends `BaseAgent`
- [ ] `__init__` calls `super().__init__(agent_role="researcher")`
- [ ] `call()` reads plan from state
- [ ] `_analyze_plan()` sends to LLM
- [ ] `_gather_data()` mocks data gathering
- [ ] `_synthesize_research()` combines data
- [ ] Returns state with "research" field
- [ ] Updated `constants.py` with researcher config
- [ ] Created test file and verified it works
- [ ] All 52 unit tests still pass

---

## **Files to Reference:**

1. **Study:** `backend/app/agents/planner.py` (structure pattern)
2. **Study:** `backend/app/agents/base.py` (parent class)
3. **Study:** `backend/test_researcher_real_llm.py` (LLM calling pattern)
4. **Modify:** `backend/app/core/constants.py` (add researcher config)
5. **Create:** `backend/app/agents/researcher.py` (your implementation)
6. **Test:** `backend/test_researcher_my_implementation.py` (verify it works)

---

## **Commands to Verify:**

```powershell
# Test your implementation
cd backend
python.exe test_researcher_my_implementation.py

# Run unit tests (should still pass)
python.exe -m pytest tests\test_researcher*.py -v

# Check for syntax errors
python.exe -m py_compile app/agents/researcher.py
```

---

## **Need Help?**

If you get stuck:
1. Look at `planner.py` for the exact pattern
2. Look at `test_researcher_real_llm.py` for LLM calling
3. Look at test files to understand expected behavior
4. Ask me - I'll help debug!

**Go build it!** 🚀
