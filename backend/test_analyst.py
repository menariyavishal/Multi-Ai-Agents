import sys
import os
from pydantic import SecretStr
from langchain_groq import ChatGroq

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

groq_key = os.getenv("GROQ_API_KEY", "")
query = "give me a fantastic project idea since i'm in my final year of btech. cse and my placement sessions are going on so i want to build a project that crazily stands out!"

prompt = f"""Analyze the research data and provide a direct, concise answer.

ORIGINAL QUERY: {query}

RESEARCH DATA:
Project ideas for computer science students with high impact and uniqueness.

Provide your output strictly in valid JSON:
{{
    "insights": ["Direct, accurate answer to the query with factual details"],
    "confidence_level": 0.95
}}"""

try:
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=SecretStr(groq_key),
        temperature=0.2
    )
    res = llm.invoke(prompt)
    print("--- ANALYST GROQ RESPONSE ---")
    print(res.content)
except Exception as e:
    print(f"Analyst Error: {e}")
