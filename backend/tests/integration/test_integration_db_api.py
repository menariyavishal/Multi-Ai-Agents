"""Integration test for db_service with API endpoints."""

import sys
sys.path.insert(0, '.')

from app import create_app
from app.services.db_service import get_db_service
import sqlite3
import json

def test_api_integration():
    """Test that API endpoints persist data to database."""
    
    print("=" * 80)
    print("TESTING DB_SERVICE INTEGRATION WITH API ENDPOINTS")
    print("=" * 80)
    
    # Create Flask test client
    app = create_app(config_name='development')
    client = app.test_client()
    
    db_service = get_db_service()
    
    # 1. Test user registration
    print("\n1. Testing user registration...")
    response = client.post(
        '/api/v1/register',
        json={
            "username": "integration_test_user",
            "email": "integration@test.com",
            "password": "Test@Password123"
        },
        content_type='application/json'
    )
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    data = response.get_json()
    api_key = data.get('api_key')
    user_id = data.get('user_id')
    
    print(f"   ✅ User registered: {user_id}")
    print(f"   ✅ API Key: {api_key[:15]}...")
    
    # Verify in database
    conn = sqlite3.connect(str(db_service.db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    assert user is not None, "User not found in database"
    print(f"   ✅ User verified in SQLite: {user['username']}")
    
    # 2. Test API key validation
    print("\n2. Testing API key validation...")
    response = client.post(
        '/api/v1/validate-key',
        json={"api_key": api_key},
        content_type='application/json'
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.get_json()
    assert data['valid'] == True, "API key should be valid"
    assert data['user_id'] == user_id, "User ID should match"
    print(f"   ✅ API key validated successfully")
    
    # 3. Test query persistence (without full workflow to save time)
    print("\n3. Testing query persistence in database...")
    test_query = "What is machine learning?"
    
    # Save a test query directly via db_service
    query_id = db_service.save_query_history(
        user_id=user_id,
        query_text=test_query,
        session_id="test_session_123",
        agent_outputs={
            "plan": "Research ML fundamentals",
            "research": "ML is...",
            "analysis": {"key_points": ["supervised", "unsupervised"]},
            "draft": "Machine learning is...",
            "review": {"score": 0.95}
        },
        status="completed",
        execution_time_seconds=10.5,
        iterations_used=2,
        quality_score=0.95
    )
    
    assert query_id is not None, "Query should be saved"
    print(f"   ✅ Query saved with ID: {query_id}")
    
    # Verify in database
    cursor.execute(
        "SELECT * FROM query_history WHERE query_id = ?",
        (query_id,)
    )
    query_record = cursor.fetchone()
    assert query_record is not None, "Query not found in database"
    assert query_record['user_id'] == user_id, "User ID should match"
    assert query_record['query_text'] == test_query, "Query text should match"
    
    # Verify agent_outputs JSON is properly stored
    agent_outputs = json.loads(query_record['agent_outputs'])
    assert agent_outputs['plan'] == "Research ML fundamentals"
    print(f"   ✅ Query verified in SQLite with structured data")
    
    # 4. Test query history retrieval
    print("\n4. Testing query history retrieval...")
    history = db_service.get_history(user_id, limit=10)
    
    assert len(history) >= 1, "Should have at least 1 query in history"
    assert history[0]['query_text'] == test_query
    assert history[0]['quality_score'] == 0.95
    print(f"   ✅ Query history retrieved: {len(history)} records")
    
    # 5. Test duplicate prevention
    print("\n5. Testing duplicate username prevention...")
    response = client.post(
        '/api/v1/register',
        json={
            "username": "integration_test_user",
            "email": "another@test.com",
            "password": "Test@Password123"
        },
        content_type='application/json'
    )
    
    assert response.status_code == 409, f"Expected 409, got {response.status_code}"
    data = response.get_json()
    assert data['status'] == 'error'
    print(f"   ✅ Duplicate prevention working")
    
    # Cleanup
    conn.close()
    
    print("\n" + "=" * 80)
    print("ALL INTEGRATION TESTS PASSED ✅")
    print("=" * 80)

if __name__ == '__main__':
    test_api_integration()
