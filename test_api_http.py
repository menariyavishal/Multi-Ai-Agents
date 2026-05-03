import requests
import json

# Make a real HTTP call to the API
url = "http://localhost:8000/api/v1/query"
data = {
    "query": "what time is it",
    "user_id": f"test_http_{__import__('random').randint(1000,9999)}"
}

print("Making HTTP request to API...")
try:
    r = requests.post(url, json=data, timeout=120)
    print(f"Response status: {r.status_code}")
    
    resp_json = r.json()
    
    analysis = resp_json.get('result', {}).get('analysis', {})
    print(f"\nAnalysis keys: {list(analysis.keys())}")
    print(f"Has 'insights'? {'insights' in analysis}")
    print(f"insights value: {analysis.get('insights', 'NOT FOUND')}")
    print(f"insights_count value: {analysis.get('insights_count', 'NOT FOUND')}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
