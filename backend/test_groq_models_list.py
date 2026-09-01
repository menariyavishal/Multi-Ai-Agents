import os
import requests

groq_key = os.getenv("GROQ_API_KEY", "")

try:
    res = requests.get(
        "https://api.groq.com/openai/v1/models",
        headers={"Authorization": f"Bearer {groq_key}"},
        timeout=10
    )
    print("Status:", res.status_code)
    data = res.json()
    print("Active Groq Models:")
    for m in data.get("data", []):
        print(f"  - {m.get('id')}")
except Exception as e:
    print(f"Error fetching models: {e}")
