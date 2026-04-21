"""Quick API test script to verify endpoints work."""

from wsgi import app
import json

def test_api():
    """Test all API endpoints."""
    
    client = app.test_client()
    
    print("\n" + "="*80)
    print("TESTING FLASK API ENDPOINTS")
    print("="*80 + "\n")
    
    # Test 1: Health check
    print("1. Testing /health endpoint...")
    response = client.get('/health')
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.get_json()}")
    assert response.status_code == 200, "Health check failed"
    print("   ✅ PASSED\n")
    
    # Test 2: Root endpoint
    print("2. Testing / (root) endpoint...")
    response = client.get('/')
    print(f"   Status: {response.status_code}")
    data = response.get_json()
    print(f"   Name: {data.get('name')}")
    print(f"   Version: {data.get('version')}")
    assert response.status_code == 200, "Root endpoint failed"
    print("   ✅ PASSED\n")
    
    # Test 3: Register endpoint (validation)
    print("3. Testing POST /api/v1/register (validation)...")
    response = client.post(
        '/api/v1/register',
        json={"username": "testuser", "email": "test@example.com", "password": "securepass123"}
    )
    print(f"   Status: {response.status_code}")
    data = response.get_json()
    print(f"   API Key Generated: {data.get('api_key', '')[:10]}...")
    assert response.status_code == 201, "Register endpoint failed"
    print("   ✅ PASSED\n")
    
    # Test 4: Validate key endpoint
    print("4. Testing POST /api/v1/validate-key...")
    response = client.post(
        '/api/v1/validate-key',
        json={"api_key": f"sk_{'a'*32}"}
    )
    print(f"   Status: {response.status_code}")
    data = response.get_json()
    print(f"   Key Valid: {data.get('valid')}")
    assert response.status_code == 200, "Validate key endpoint failed"
    print("   ✅ PASSED\n")
    
    # Test 5: Query endpoint (validation only, no actual processing)
    print("5. Testing POST /api/v1/query (validation)...")
    response = client.post(
        '/api/v1/query',
        json={}
    )
    print(f"   Status: {response.status_code} (expected 400 for empty query)")
    assert response.status_code == 400, "Query validation failed"
    print("   ✅ PASSED\n")
    
    # Test 6: History endpoint
    print("6. Testing GET /api/v1/history/<query>...")
    response = client.get('/api/v1/history/test_query')
    print(f"   Status: {response.status_code}")
    data = response.get_json()
    print(f"   Checkpoints Found: {len(data.get('checkpoints', []))}")
    assert response.status_code == 200, "History endpoint failed"
    print("   ✅ PASSED\n")
    
    # Test 7: 404 error handling
    print("7. Testing 404 error handling...")
    response = client.get('/nonexistent/endpoint')
    print(f"   Status: {response.status_code}")
    assert response.status_code == 404, "404 handling failed"
    print("   ✅ PASSED\n")
    
    print("="*80)
    print("ALL TESTS PASSED ✅")
    print("="*80)

if __name__ == "__main__":
    test_api()
