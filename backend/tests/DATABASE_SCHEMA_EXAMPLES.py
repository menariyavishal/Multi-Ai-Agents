#!/usr/bin/env python3
"""
DATABASE SCHEMA & RESPONSE EXAMPLES
Shows exactly what gets stored and how agents interact with it
"""

import json
from datetime import datetime

print('='*90)
print('DATABASE SCHEMA & AGENT INTEGRATION EXAMPLES')
print('='*90)
print()

# PART 1: DATABASE SCHEMA
print('[PART 1] MONGODB DOCUMENT STRUCTURE')
print('-'*90)
print()
print('When a conversation is saved, MongoDB stores a document like this:')
print()

example_conversation = {
    "_id": "507f1f77bcf86cd799439011",  # MongoDB ObjectId
    "user_id": "test_user_001",
    "conversation_id": "conv_2024_04_25_001",
    "query": "What are the latest trends in artificial intelligence?",
    "plan": {
        "steps": [
            "Research current AI trends",
            "Analyze key areas",
            "Identify market impacts"
        ],
        "estimated_sources": 5,
        "data_type": "COMBINED"
    },
    "research": {
        "sources_used": ["wikipedia", "news_api", "google_custom_search", "database"],
        "data_type": "COMBINED",
        "synthesis": "Combined analysis of real-time data with historical context...",
        "source_count": 4,
        "section_count": 4
    },
    "analysis": {
        "data_classification": "COMBINED",
        "patterns": [
            "Increasing adoption of AI in enterprises",
            "Focus on ethical AI and explainability"
        ],
        "statistics": {
            "trend_count": 8,
            "pattern_count": 1
        },
        "insights": [
            {
                "insight": "Generative AI is becoming mainstream",
                "confidence": 0.85,
                "sources": 2
            },
            {
                "insight": "AI regulation is increasing globally",
                "confidence": 0.72,
                "sources": 1
            },
            {
                "insight": "Multimodal AI models gaining traction",
                "confidence": 0.65,
                "sources": 1
            }
        ],
        "recommendations": [
            "Monitor emerging AI regulations",
            "Invest in AI literacy programs",
            "Consider AI integration strategies",
            "Evaluate data privacy implications",
            "Plan for AI infrastructure needs"
        ],
        "quality_score": 0.82,
        "coverage_expected": 1.0
    },
    "draft": {
        "executive_summary": "Latest AI trends show continued growth in...",
        "main_body": "The AI landscape in 2024 is characterized by...",
        "recommendations_section": "Organizations should consider...",
        "conclusion": "The trajectory of AI development suggests...",
        "total_chars": 2671,
        "sections": 4
    },
    "review_feedback": [
        {
            "iteration": 1,
            "decision": "NEEDS_REVISION",
            "quality_score": 0.76,
            "issues": [],
            "feedback": "Content could be more comprehensive"
        },
        {
            "iteration": 2,
            "decision": "NEEDS_REVISION",
            "quality_score": 0.78,
            "issues": [],
            "feedback": "Adding more market data would strengthen"
        },
        {
            "iteration": 3,
            "decision": "APPROVED",
            "quality_score": 0.80,
            "issues": [],
            "feedback": "Final version meets quality standards"
        }
    ],
    "messages": [
        {
            "type": "HumanMessage",
            "content": "What are the latest trends in artificial intelligence?",
            "agent": "user"
        },
        {
            "type": "AIMessage",
            "content": "Plan generated with 3 research steps",
            "agent": "planner"
        },
        {
            "type": "AIMessage",
            "content": "Research synthesized from 4 sources (877 chars)",
            "agent": "researcher"
        },
        {
            "type": "AIMessage",
            "content": "Analysis complete: 8 metrics, 3 insights, 5 recommendations",
            "agent": "analyst"
        },
        {
            "type": "AIMessage",
            "content": "Final draft compiled: Executive summary + body + recommendations + conclusion",
            "agent": "writer"
        },
        {
            "type": "AIMessage",
            "content": "Review complete: 0 structure issues, 0 data issues, Quality: 0.80",
            "agent": "reviewer"
        }
    ],
    "final_answer": "Based on comprehensive research and analysis, the latest AI trends include...",
    "metadata": {
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "total_iterations": 3,
        "total_execution_time_seconds": 4.79,
        "status": "completed",
        "agents_executed": ["planner", "researcher", "analyst", "writer", "reviewer"]
    }
}

print(json.dumps(example_conversation, indent=2, default=str)[:2000] + "...")
print()
print()

# PART 2: HOW AGENTS USE THE DATABASE
print('[PART 2] AGENT DATABASE INTERACTIONS')
print('-'*90)
print()

interactions = {
    "PLANNER": {
        "writes_to_db": ["plan"],
        "reads_from_db": [],
        "why": "Planner is first agent, doesn't need historical data"
    },
    "RESEARCHER": {
        "writes_to_db": ["research"],
        "reads_from_db": ["past_conversations", "similar_queries"],
        "how": "Checks database for past conversations on similar topics",
        "example": {
            "query_needed": "AI trends",
            "db_search": "Find conversations where topic matches 'AI'",
            "result": "Found 3 past conversations on AI",
            "use": "Combines with real-time data (Wikipedia, News, Google)"
        }
    },
    "ANALYST": {
        "writes_to_db": ["analysis"],
        "reads_from_db": [],
        "why": "Analyst processes fresh research, doesn't need DB"
    },
    "WRITER": {
        "writes_to_db": ["draft"],
        "reads_from_db": [],
        "why": "Writer uses analyst output, doesn't need DB"
    },
    "REVIEWER": {
        "writes_to_db": ["review_feedback"],
        "reads_from_db": [],
        "why": "Reviewer validates current work, doesn't need DB"
    },
    "WORKFLOW": {
        "writes_to_db": ["full_conversation"],
        "writes_at": "End of workflow (after reviewer)",
        "writes": [
            "user_id",
            "conversation_id",
            "query",
            "plan",
            "research",
            "analysis",
            "draft",
            "review_feedback",
            "messages",
            "final_answer",
            "metadata"
        ],
        "enables": "Users can retrieve conversation history"
    }
}

for agent, details in interactions.items():
    print(f"[{agent}]")
    for key, value in details.items():
        if isinstance(value, list):
            print(f"  {key}:")
            for item in value:
                print(f"    • {item}")
        elif isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")
    print()

print()

# PART 3: RESPONSE STRUCTURE
print('[PART 3] API RESPONSE EXAMPLES')
print('-'*90)
print()

# Query Response
print('A. POST /api/v1/query - Response Example:')
print()
query_response = {
    "status": "completed",
    "conversation_id": "conv_2024_04_25_001",
    "session_id": "sess_2024_04_25_001",
    "user_id": "test_user_001",
    "query": "What are the latest AI trends?",
    "result": {
        "final_answer": "Based on comprehensive research...",
        "summary": "3 main trends identified...",
        "key_points": [
            "Generative AI mainstream",
            "Regulation increasing",
            "Multimodal models gaining traction"
        ]
    },
    "metadata": {
        "execution_time_seconds": 4.79,
        "agents_used": 5,
        "iterations": 3,
        "final_quality_score": 0.80,
        "status": "approved"
    }
}
print(json.dumps(query_response, indent=2))
print()
print()

# History Response
print('B. GET /api/v1/history?user_id=test_user_001 - Response Example:')
print()
history_response = {
    "user_id": "test_user_001",
    "total_conversations": 5,
    "conversations": [
        {
            "conversation_id": "conv_2024_04_25_001",
            "query": "What are the latest AI trends?",
            "created_at": "2024-04-25T10:30:00",
            "status": "completed",
            "quality_score": 0.80
        },
        {
            "conversation_id": "conv_2024_04_24_005",
            "query": "How is AI being used in healthcare?",
            "created_at": "2024-04-24T15:45:00",
            "status": "completed",
            "quality_score": 0.85
        },
        {
            "conversation_id": "conv_2024_04_24_001",
            "query": "Explain machine learning",
            "created_at": "2024-04-24T09:15:00",
            "status": "completed",
            "quality_score": 0.88
        }
    ]
}
print(json.dumps(history_response, indent=2))
print()
print()

# Specific Conversation Response
print('C. GET /api/v1/conversation/conv_2024_04_25_001 - Response Example:')
print()
conversation_response = {
    "conversation_id": "conv_2024_04_25_001",
    "user_id": "test_user_001",
    "query": "What are the latest AI trends?",
    "workflow_results": {
        "planner_output": "3 research steps identified",
        "researcher_output": "Data from 4 sources synthesized",
        "analyst_output": "8 metrics, 3 insights extracted",
        "writer_output": "Professional report generated",
        "reviewer_output": "Quality score: 0.80, Approved"
    },
    "final_answer": "Based on comprehensive research...",
    "metadata": {
        "created_at": "2024-04-25T10:30:00",
        "completed_at": "2024-04-25T10:34:48",
        "total_time": 4.79,
        "iterations": 3
    }
}
print(json.dumps(conversation_response, indent=2))
print()
print()

# Search Response
print('D. GET /api/v1/search?query=AI - Response Example:')
print()
search_response = {
    "query": "AI",
    "total_results": 12,
    "results": [
        {
            "conversation_id": "conv_2024_04_25_001",
            "user_id": "test_user_001",
            "query": "What are the latest AI trends?",
            "match_score": 0.98,
            "created_at": "2024-04-25T10:30:00"
        },
        {
            "conversation_id": "conv_2024_04_24_005",
            "user_id": "test_user_001",
            "query": "How is AI being used in healthcare?",
            "match_score": 0.95,
            "created_at": "2024-04-24T15:45:00"
        },
        {
            "conversation_id": "conv_2024_04_23_003",
            "user_id": "test_user_002",
            "query": "Explain machine learning and AI",
            "match_score": 0.92,
            "created_at": "2024-04-23T11:20:00"
        }
    ]
}
print(json.dumps(search_response, indent=2))
print()
print()

# PART 4: DATA FLOW EXAMPLES
print('[PART 4] DATA FLOW EXAMPLES - STEP BY STEP')
print('-'*90)
print()

print('EXAMPLE 1: How Database Data Flows to Researcher')
print()
print('Step 1: User sends query')
print('  Input: "What are the latest AI trends?"')
print('  user_id: test_user_001')
print()
print('Step 2: Planner runs')
print('  Creates plan with research steps')
print('  ✓ Plan stored in state')
print()
print('Step 3: Researcher runs')
print('  3a. Checks database:')
print('      Query: "Find conversations where topic ≈ AI trends"')
print('      Result: Found 3 past conversations')
print('      Extracts insights from past data')
print()
print('  3b. Fetches real-time data:')
print('      - Wikipedia: "Artificial Intelligence - Recent developments"')
print('      - News API: "Latest AI breakthroughs in 2024"')
print('      - Google Custom Search: "AI trends 2024"')
print()
print('  3c. Synthesizes combined data:')
print('      "The latest AI trends (from both historical & real-time data) include..."')
print('      ✓ Research stored in state')
print()
print('Step 4: Analyst processes')
print('  Takes research from state')
print('  Extracts patterns and statistics')
print('  ✓ Analysis stored in state')
print()
print('Step 5: Writer creates')
print('  Takes analysis from state')
print('  Writes professional content')
print('  ✓ Draft stored in state')
print()
print('Step 6: Reviewer validates')
print('  Takes draft from state')
print('  Validates quality')
print('  ✓ Feedback stored in state')
print()
print('Step 7: Workflow completes')
print('  ALL state data saved to MongoDB:')
print('    • user_id: test_user_001')
print('    • plan: [from step 2]')
print('    • research: [from step 3]')
print('    • analysis: [from step 4]')
print('    • draft: [from step 5]')
print('    • review_feedback: [from step 6]')
print()
print('Step 8: User retrieves history')
print('  GET /api/v1/history?user_id=test_user_001')
print('  Returns: All conversations for this user (including this one)')
print()
print()

# PART 5: KEY DATABASE FEATURES
print('[PART 5] KEY DATABASE FEATURES IN ACTION')
print('-'*90)
print()

features = {
    "1. Multi-User Support": {
        "how_it_works": "Each conversation tied to user_id",
        "example": "GET /api/v1/history?user_id=test_user_001 returns only that user's conversations",
        "benefit": "Multiple users can use system simultaneously"
    },
    "2. Conversation Continuity": {
        "how_it_works": "All agent outputs stored together",
        "example": "Can retrieve entire workflow for a conversation",
        "benefit": "Users can see complete reasoning path"
    },
    "3. Historical Context": {
        "how_it_works": "Researcher searches past conversations",
        "example": "If user asks AI question, Researcher finds all past AI conversations",
        "benefit": "System learns from previous interactions"
    },
    "4. Searchability": {
        "how_it_works": "MongoDB full-text search on query and content",
        "example": "Search for 'AI' returns all AI-related conversations",
        "benefit": "Users can find past conversations easily"
    },
    "5. Quality Tracking": {
        "how_it_works": "Each conversation stores quality_score",
        "example": "Can retrieve high-quality conversations for reference",
        "benefit": "Identify which conversations are most useful"
    },
    "6. Audit Trail": {
        "how_it_works": "Each message/iteration stored",
        "example": "Can see all 3 iterations of Reviewer feedback",
        "benefit": "Complete transparency in processing"
    }
}

for feature, details in features.items():
    print(f"{feature}")
    for key, value in details.items():
        print(f"  • {key}: {value}")
    print()

print()
print('='*90)
print('DATABASE INTEGRATION COMPLETE AND OPERATIONAL ✓')
print('='*90)
