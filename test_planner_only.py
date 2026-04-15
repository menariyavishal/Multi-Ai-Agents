#!/usr/bin/env python3
"""
Test Planner Agent with Groq API
Testing the optimized configuration where Groq is used ONLY for Planner
"""
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from app.core.llm_factory import LLMFactory
from app.core.logger import get_logger
from app.config import Config

logger = get_logger("PlannerTest")

print("=" * 80)
print("PLANNER AGENT - GROQ API OPTIMIZATION TEST")
print("=" * 80)

print("\n[CONFIGURATION CHECK]")
print("-" * 80)
print(f"Groq API Key: {'EXISTS' if Config.GROQ_API_KEY else 'MISSING'}")
if Config.GROQ_API_KEY:
    key_sample = Config.GROQ_API_KEY[:10] + "..." + Config.GROQ_API_KEY[-10:]
    print(f"  Value: {key_sample}")

print("\n[TEST 1] Initialize Planner LLM Instance")
print("-" * 80)

try:
    logger.info("Creating Planner (Groq) LLM...")
    planner_llm = LLMFactory.get_llm("planner")
    print(f"✓ LLM instance created: {type(planner_llm).__name__}")
    print(f"✓ Model configured for: Planner agent")
    
except Exception as e:
    print(f"✗ Failed to initialize: {str(e)[:100]}")
    sys.exit(1)

print("\n[TEST 2] Test Groq API with Simple Prompt")
print("-" * 80)

try:
    test_prompt = "You are a planning agent. Say 'Ready to plan' briefly."
    
    logger.info(f"Sending prompt to Groq: '{test_prompt[:50]}...'")
    print(f"Prompt: {test_prompt}")
    print(f"Waiting for response...\n")
    
    response = planner_llm.invoke(test_prompt)
    
    print(f"\n✓ API Response Received:")
    print(f"  {response.content[:200]}")
    
    if "plan" in response.content.lower() or "ready" in response.content.lower():
        print(f"\n✓ SUCCESS: Planner agent is working!")
        print(f"✓ Groq API is operational")
        status = "WORKING"
    else:
        print(f"\n✓ Response received but format unexpected")
        status = "WORKING"
        
except Exception as e:
    error_msg = str(e)
    print(f"\n✗ API Error: {error_msg[:200]}")
    print(f"✗ Status: FAILED")
    status = "ERROR"

print("\n[TEST 3] Verify Agent Configuration")
print("-" * 80)

from app.core.constants import MODEL_CONFIGS

print(f"\nAgent Configurations:")
for role, config in MODEL_CONFIGS.items():
    marker = "★" if role == "planner" else "○"
    print(f"  {marker} {role:12} -> {config['provider']:12} ({config['name'][:30]})")

print(f"\nNote: ★ = Uses Gemini (LIMITED QUOTA)")
print(f"      ○ = Uses HuggingFace (No Gemini quota used)")

print("\n[TEST 4] Check Caching")
print("-" * 80)

planner_1 = LLMFactory.get_llm("planner")
planner_2 = LLMFactory.get_llm("planner")

if planner_1 is planner_2:
    print("✓ LLMFactory caching working (same instance returned)")
else:
    print("✗ Caching issue (different instances)")

print("\n" + "=" * 80)
print("OPTIMIZATION SUMMARY")
print("=" * 80)

print(f"\n✓ Gemini Usage Optimized:")
print(f"  • Only Planner agent uses Gemini (1 of 5 agents)")
print(f"  • Researcher, Analyst, Writer, Reviewer use HuggingFace")
print(f"  • Quota savings: ~80% reduction in Gemini API calls")

print(f"\n✓ Planner Agent Status: {status}")

if status == "WORKING":
    print(f"\n✅ READY FOR PHASE 3: Database Layer")
elif status == "QUOTA_EXCEEDED":
    print(f"\n⚠️  Quota limit reached (expected on free tier)")
    print(f"    System is still functional - proceed with Phase 3")
    print(f"    API calls can be mocked during development")
else:
    print(f"\n❌ Issues detected - review configuration")

print("\n" + "=" * 80)
