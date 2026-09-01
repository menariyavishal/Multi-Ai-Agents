import os

keys_to_check = [
    "GROQ_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY", 
    "GOOGLE_API_KEY", "TAVILY_API_KEY", "SERPAPI_API_KEY", "ANTHROPIC_API_KEY"
]

found = {}
for k in keys_to_check:
    val = os.getenv(k)
    if val and val != "your_groq_api_key_here":
        found[k] = val[:8] + "..."
    else:
        found[k] = "Not Set"

print("Environment Keys Check:")
for k, v in found.items():
    print(f"  {k}: {v}")
