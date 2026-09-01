import urllib.request
import json

url = "http://127.0.0.1:5000/api/v1/query"
payload = json.dumps({
    "query": "give me a fantastic project idea since i'm in my final year of btech. cse and my placement sessions are going on so i want to build a project that crazily stands out!",
    "user_id": "dalia",
    "max_iterations": 1
}).encode("utf-8")

req = urllib.request.Request(
    url,
    data=payload,
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode("utf-8"))
        res = data.get('result', {})
        print("KEYS IN RESULT:", list(res.keys()))
        print("\n--- FINAL ANSWER ---")
        print(str(res.get('final_answer'))[:500])
except Exception as e:
    print(f"FAILED: {e}")
