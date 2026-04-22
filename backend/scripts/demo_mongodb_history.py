#!/usr/bin/env python3
"""
Demo script showing how to use MongoDB conversation history with the Multi-AI Agents API.

This script demonstrates:
1. Making queries to the API and automatically saving to MongoDB
2. Retrieving conversation history
3. Searching conversations
4. Getting user statistics

Usage:
    python demo_mongodb_history.py
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:5000/api/v1"
USER_ID = "demo_user_123"


def pretty_print(title: str, data: Dict[str, Any]):
    """Pretty print JSON response."""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    print(json.dumps(data, indent=2, default=str))


def demo_save_conversation():
    """Demo: Save a conversation by making a query."""
    print("\n🔄 Demo 1: Querying and Saving to MongoDB")
    print("-" * 60)
    
    query_data = {
        "query": "What are the latest AI trends in 2024?",
        "user_id": USER_ID,
        "max_iterations": 2
    }
    
    print(f"📤 Sending query to {API_BASE_URL}/query")
    print(f"User ID: {USER_ID}")
    print(f"Query: {query_data['query']}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json=query_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            pretty_print("Query Response", result)
            
            if result.get("status") == "success":
                conversation_id = result.get("conversation_id")
                print(f"\n✅ Conversation saved to MongoDB!")
                print(f"Conversation ID: {conversation_id}")
                
                return conversation_id
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is the Flask server running on localhost:5000?")
    except requests.exceptions.Timeout:
        print("⏱️  Request timed out. The query took too long.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    return None


def demo_get_history():
    """Demo: Retrieve conversation history for a user."""
    print("\n🔄 Demo 2: Retrieving Conversation History")
    print("-" * 60)
    
    print(f"📤 Getting history for user: {USER_ID}")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/history",
            params={
                "user_id": USER_ID,
                "limit": 5,
                "skip": 0
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            pretty_print("Conversation History", result)
            
            conversations = result.get("conversations", [])
            if conversations:
                return conversations[0]["conversation_id"]
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    return None


def demo_get_specific_conversation(conversation_id: str):
    """Demo: Get full details of a specific conversation."""
    print("\n🔄 Demo 3: Retrieving Specific Conversation")
    print("-" * 60)
    
    if not conversation_id:
        print("⚠️  No conversation_id provided. Skipping...")
        return
    
    print(f"📤 Getting conversation: {conversation_id}")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/conversation/{conversation_id}",
            params={"user_id": USER_ID}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("status") == "success":
                conv = result.get("conversation", {})
                
                print("\n📖 Full Conversation Details:")
                print(f"  Query: {conv.get('query')}")
                print(f"  Quality Score: {conv.get('quality_score')}")
                print(f"  Quality Level: {conv.get('quality_level')}")
                print(f"  Data Classification: {conv.get('data_classification')}")
                print(f"  Processing Time: {conv.get('processing_time_seconds')}s")
                print(f"  Created At: {conv.get('created_at')}")
                print(f"  Tags: {conv.get('tags')}")
                
                # Show summary of content
                content = conv.get('final_output', '')
                if content:
                    print(f"\n📝 Content Preview (first 200 chars):")
                    print(f"  {content[:200]}...")
                
                return conv
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    return None


def demo_search_conversations():
    """Demo: Search conversations by keyword."""
    print("\n🔄 Demo 4: Searching Conversations")
    print("-" * 60)
    
    search_term = "AI"
    print(f"📤 Searching for conversations containing: '{search_term}'")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/search",
            params={
                "user_id": USER_ID,
                "q": search_term,
                "limit": 5
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            pretty_print("Search Results", result)
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def demo_get_statistics():
    """Demo: Get user statistics."""
    print("\n🔄 Demo 5: User Statistics")
    print("-" * 60)
    
    print(f"📤 Getting statistics for user: {USER_ID}")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/stats",
            params={"user_id": USER_ID}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("status") == "success":
                stats = result.get("stats", {})
                
                print("\n📊 User Statistics:")
                print(f"  Total Conversations: {stats.get('total_conversations')}")
                print(f"  Total Queries: {stats.get('total_queries')}")
                print(f"  Average Quality Score: {stats.get('average_quality_score'):.2f}")
                print(f"  Last Query At: {stats.get('last_query_at')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def main():
    """Run all demos."""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   Multi-AI Agents - MongoDB Conversation History Demo    ║
    ║                 ChatGPT-like Chat History                ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    print("📌 Prerequisites:")
    print("  1. Flask API running on http://localhost:5000")
    print("  2. MongoDB running (local or Atlas)")
    print("  3. Python requests library installed")
    print("")
    
    # Demo flow
    print("Starting demos...\n")
    
    # 1. Save a conversation
    print("Step 1️⃣ : Querying the API (saves to MongoDB automatically)")
    conv_id = demo_save_conversation()
    
    if not conv_id:
        print("\n⚠️  Failed to save conversation. Check if API and MongoDB are running.")
        return
    
    # Wait for user confirmation to proceed
    input("\nPress ENTER to continue to next demo...")
    
    # 2. Get history
    print("\nStep 2️⃣ : Retrieving conversation history")
    history_conv_id = demo_get_history()
    
    # Use the conversation_id from history if available, otherwise use the one we just created
    target_conv_id = history_conv_id or conv_id
    
    input("\nPress ENTER to continue to next demo...")
    
    # 3. Get specific conversation
    print("\nStep 3️⃣ : Getting full conversation details")
    demo_get_specific_conversation(target_conv_id)
    
    input("\nPress ENTER to continue to next demo...")
    
    # 4. Search
    print("\nStep 4️⃣ : Searching conversations")
    demo_search_conversations()
    
    input("\nPress ENTER to continue to next demo...")
    
    # 5. Statistics
    print("\nStep 5️⃣ : Getting user statistics")
    demo_get_statistics()
    
    print("\n" + "="*60)
    print("✅ Demo Complete!")
    print("="*60)
    print(f"""
Your conversation history is now stored in MongoDB!

💾 Stored Conversation ID: {target_conv_id}
👤 User ID: {USER_ID}

🔗 Try these URLs in your browser:
  - Get history: /api/v1/history?user_id={USER_ID}
  - Get one: /api/v1/conversation/{target_conv_id}?user_id={USER_ID}
  - Search: /api/v1/search?user_id={USER_ID}&q=AI
  - Stats: /api/v1/stats?user_id={USER_ID}

📚 For more details, see MONGODB_SETUP.md in project root
    """)


if __name__ == "__main__":
    main()
