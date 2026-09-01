import os
from pydantic import SecretStr
from langchain_groq import ChatGroq

groq_key = os.getenv("GROQ_API_KEY", "")

models_to_test = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
    "groq/compound"
]

for model_name in models_to_test:
    print(f"\nTesting model: '{model_name}'...")
    try:
        llm = ChatGroq(
            model=model_name,
            api_key=SecretStr(groq_key),
            temperature=0.3
        )
        res = llm.invoke("What is 25 * 4 and what is the capital of Japan?")
        print(f"SUCCESS with {model_name}!")
        print("Response:", res.content)
        break
    except Exception as e:
        print(f"Error with {model_name}: {e}")
