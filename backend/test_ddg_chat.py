import requests
import ssl

def test_ddg_ai(prompt: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/event-stream',
        'x-vqd-accept': '1'
    }
    
    session = requests.Session()
    session.verify = False
    
    # Step 1: Get VQD token
    try:
        resp = session.get('https://duckduckgo.com/duckduckgo-help-pages/', headers=headers, timeout=5)
        vqd = resp.headers.get('x-vqd-4')
        if not vqd:
            resp2 = session.post('https://duckduckgo.com/duckchat/v1/status', headers=headers, timeout=5)
            vqd = resp2.headers.get('x-vqd-4')
        print(f"VQD Token: {vqd}")
    except Exception as e:
        print(f"VQD error: {e}")
        vqd = None
        
    return vqd

if __name__ == "__main__":
    v = test_ddg_ai("Hello")
