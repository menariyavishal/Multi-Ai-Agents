import urllib.request
import urllib.parse
import re
import json
import ssl

ssl_context = ssl._create_unverified_context()

def search_web_realtime(query: str):
    print(f"Searching web in real-time for: '{query}'...")
    results = []
    
    # 1. Try DuckDuckGo HTML Search
    try:
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        })
        with urllib.request.urlopen(req, context=ssl_context, timeout=6) as response:
            html = response.read().decode('utf-8', errors='ignore')
            snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
            for snip in snippets[:5]:
                clean_text = re.sub(r'<[^>]+>', '', snip).strip()
                if clean_text:
                    results.append(clean_text)
    except Exception as e:
        print(f"DuckDuckGo error: {e}")

    # 2. Try Wikipedia API Search
    if not results:
        try:
            wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json"
            req = urllib.request.Request(wiki_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ssl_context, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                for item in data.get('query', {}).get('search', [])[:4]:
                    clean_snippet = re.sub(r'<[^>]+>', '', item.get('snippet', ''))
                    results.append(f"{item.get('title')}: {clean_snippet}")
        except Exception as e:
            print(f"Wikipedia error: {e}")
            
    return results

if __name__ == "__main__":
    res = search_web_realtime("latest AI trends 2026")
    print(f"\nFound {len(res)} results:")
    for i, r in enumerate(res, 1):
        print(f"{i}. {r}\n")
