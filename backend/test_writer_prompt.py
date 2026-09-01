import sys
import os
from pydantic import SecretStr
from langchain_groq import ChatGroq

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

groq_key = os.getenv("GROQ_API_KEY", "")
query = "give me a fantastic project idea since i'm in my final year of btech. cse and my placement sessions are going on so i want to build a project that crazily stands out!"

prompt = f"""You are an elite AI assistant (like ChatGPT or Claude). Write an outstanding, detailed, and comprehensive response to the user's request.

USER REQUEST: {query}

Provide a direct, highly detailed, innovative, and thorough answer immediately.
DO NOT echo or repeat the user's question ("Answer for...", "Query:", etc.).
DO NOT output any metadata labels, prompt text, or debugging bullet points.
Structure your response cleanly with clear headings, bullet points, and actionable details that make it stand out."""

try:
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=SecretStr(groq_key),
        temperature=0.3
    )
    res = llm.invoke(prompt)
    print("--- GROQ 120B GENERATION ---")
    print(res.content[:1000])
except Exception as e:
    print(f"Error: {e}")
