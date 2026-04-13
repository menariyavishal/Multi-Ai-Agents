#!/usr/bin/env python3
"""
QUICK START GUIDE - Nueuro-Agents Phase 2

How to use the LLM system for different scenarios
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    NUEURO-AGENTS - QUICK START GUIDE                       ║
║                         Phase 2 Infrastructure                             ║
╚════════════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════════════
SCENARIO 1: Development & Testing (Recommended for Phase 3)
═══════════════════════════════════════════════════════════════════════════════

COMMAND:
    export USE_MOCK_LLM=true
    python test_phase2.py

FEATURES:
    ✓ No API calls
    ✓ No quota usage
    ✓ Instant responses
    ✓ Deterministic testing
    ✓ All 5 agents working
    
USE WHEN:
    • Building Phase 3 (Database Layer)
    • Writing tests
    • Developing features
    • Running CI/CD pipelines
    • Debugging workflows

═══════════════════════════════════════════════════════════════════════════════
SCENARIO 2: Production with Paid APIs
═══════════════════════════════════════════════════════════════════════════════

SETUP:
    1. Upgrade Gemini to paid plan (Google Cloud Console)
    2. Update .env with paid API keys:
       GEMINI_API_KEY=your_paid_gemini_key
       HF_API_TOKEN=your_valid_hf_token
    3. Unset mock mode (or set to false)

COMMAND:
    unset USE_MOCK_LLM
    python -c "from app.core.llm_factory import LLMFactory; llm = LLMFactory.get_llm('planner'); print(llm.invoke('Your prompt'))"

FEATURES:
    ✓ Real Gemini API (Planner agent only)
    ✓ HuggingFace for other agents
    ✓ Production-quality responses
    ✓ Full agent capabilities
    • Higher latency
    • Requires paid subscription
    • Higher API quota

═══════════════════════════════════════════════════════════════════════════════
SCENARIO 3: Run Optimized Planner Test
═══════════════════════════════════════════════════════════════════════════════

COMMAND:
    python test_planner_only.py

WHAT IT DOES:
    • Tests Planner agent (Gemini only)
    • Shows quota status
    • Displays optimization benefits
    • Single-agent focused test

STATUS:
    Currently: QUOTA_EXCEEDED (free tier)
    Solution: Upgrade or use Mock LLMs

═══════════════════════════════════════════════════════════════════════════════
SCENARIO 4: Full Mock LLM Agent Test
═══════════════════════════════════════════════════════════════════════════════

COMMAND:
    python test_mock_llms.py

WHAT IT TESTS:
    ✓ All 5 agents initialized
    ✓ Each agent responds correctly  
    ✓ LLM Factory caching verified
    ✓ Mock response accuracy

EXPECTED OUTPUT:
    • 5/5 agents passing
    • Caching verification
    • Ready for Phase 3 message

═══════════════════════════════════════════════════════════════════════════════
CODE USAGE EXAMPLES
═══════════════════════════════════════════════════════════════════════════════

Example 1: Simple agent invocation
────────────────────────────────────
    import os
    os.environ["USE_MOCK_LLM"] = "true"
    
    from app.core.llm_factory import LLMFactory
    
    planner = LLMFactory.get_llm("planner")
    response = planner.invoke("What should we do?")
    print(response)

Example 2: All agents
──────────────────────
    agents = ["planner", "researcher", "analyst", "writer", "reviewer"]
    
    for agent in agents:
        llm = LLMFactory.get_llm(agent)
        response = llm.invoke("Hello from {}".format(agent))
        print(f"{agent}: {response}")

Example 3: Production code
───────────────────────────
    # In your workflow/agent code
    from app.core.llm_factory import LLMFactory
    from app.core.logger import get_logger
    
    logger = get_logger(__name__)
    
    class MyAgent:
        def __init__(self):
            self.llm = LLMFactory.get_llm("planner")
            logger.info("Agent initialized")
        
        def run(self, prompt):
            logger.info(f"Processing: {prompt[:50]}...")
            response = self.llm.invoke(prompt)
            logger.info(f"Response: {response.content[:50]}...")
            return response

═══════════════════════════════════════════════════════════════════════════════
ENVIRONMENT VARIABLES
═══════════════════════════════════════════════════════════════════════════════

Set in .env file:
    GEMINI_API_KEY=your_key           # Google Gemini API key
    HF_API_TOKEN=your_token           # HuggingFace API token
    SECRET_KEY=your_secret            # Flask secret
    LLM_TIMEOUT=30                    # API timeout in seconds
    LLM_MAX_RETRIES=2                 # Retry attempts
    USE_MOCK_LLM=true                 # Enable mock LLMs for dev
    SQLITE_PATH=data/nueuro.db        # SQLite database path

═══════════════════════════════════════════════════════════════════════════════
TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════════

Problem: "RESOURCE_EXHAUSTED 429 error"
Solution: 
    • You hit Gemini free tier quota
    • Use Mock LLMs: SET USE_MOCK_LLM=true
    • Upgrade to paid plan for production

Problem: "HF_API_TOKEN is not set"
Solution:
    • Add HF_API_TOKEN to .env
    • Or use Mock LLMs for development

Problem: "Module not found" errors
Solution:
    • Ensure Python path includes 'backend' folder
    • Check pyrightconfig.json configuration
    • Verify __init__.py files exist in all directories

Problem: Type checking errors in IDE
Solution:
    • Reload VS Code (Cmd+Shift+P → "Reload Window")
    • Check .vscode/settings.json
    • Verify pyrightconfig.json

═══════════════════════════════════════════════════════════════════════════════
RECOMMENDED WORKFLOW FOR PHASE 3
═══════════════════════════════════════════════════════════════════════════════

1. Development & Building:
   SET USE_MOCK_LLM=true
   [Build database layer, test workflows, etc.]
   python test_phase2.py  ← Verify infrastructure

2. Testing:
   python test_mock_llms.py  ← Test all agents
   python test_phase2.py     ← Full suite

3. Pre-Production:
   [Upgrade API plans if needed]
   UNSET USE_MOCK_LLM
   [Update .env with paid keys]
   [Run integration tests]

4. Production:
   Deploy with paid API keys
   Monitor quota usage
   Scale as needed

═══════════════════════════════════════════════════════════════════════════════
PHASE 2 STATUS: COMPLETE ✅

All infrastructure is ready for Phase 3 (Database Layer)

Next: Start Phase 3 - Database Layer
    • SQLite schema
    • MongoDB setup
    • CRUD operations
    • Data models

═══════════════════════════════════════════════════════════════════════════════
""")
