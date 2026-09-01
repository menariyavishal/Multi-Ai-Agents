import urllib.request
import urllib.parse
import json
import ssl

ssl_ctx = ssl._create_unverified_context()

def ask_real_ai(prompt: str):
    print(f"Sending prompt to Real AI model: '{prompt}'...")
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://text.pollinations.ai/{encoded_prompt}"
    
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0'
    })
    
    try:
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=12) as response:
            answer = response.read().decode('utf-8')
            return answer
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    test_q = "What is the capital of France and what is 25 * 4?"
    ans = ask_real_ai(test_q)
    print("\n--- REAL AI RESPONSE ---")
    print(ans)
