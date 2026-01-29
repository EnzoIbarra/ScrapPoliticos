
import json
import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def search_duckduckgo(query):
    """Búsqueda simple usando DuckDuckGo HTML (sin API key)."""
    try:
        url = f"https://html.duckduckgo.com/html/?q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # El primer resultado orgánico suele estar en un div con clase 'result__body' -> 'a.result__a'
            results = soup.select('a.result__a')
            if results:
                return results[0]['href']
    except Exception as e:
        print(f"Error buscando {query}: {e}")
    return None

def fix_urls():
    retry_file = Path("data/retry_queue.json")
    if not retry_file.exists():
        print("No hay cola de reintento.")
        return

    with open(retry_file, 'r', encoding='utf-8') as f:
        queue = json.load(f)

    print(f"🔍 Buscando URLs correctas para {len(queue)} municipios...")
    
    updated_count = 0
    for item in queue:
        muni = item['municipality']
        old_url = item['url']
        
        # Búsqueda: "Ayuntamiento de [Municipio] sitio oficial"
        query = f"Ayuntamiento de {muni} sitio oficial"
        new_url = search_duckduckgo(query)
        
        if new_url and new_url != old_url:
            # Validar que no sea un PDF o Facebook si es posible, pero confiamos en el primer resultado
            print(f"✅ {muni}: {old_url} -> {new_url}")
            item['url'] = new_url
            updated_count += 1
            # Rate limiting respetuoso
            time.sleep(2)
        else:
            print(f"⚠️ {muni}: No se encontró mejor URL o es la misma.")
            time.sleep(1)

    with open(retry_file, 'w', encoding='utf-8') as f:
        json.dump(queue, f, indent=4, ensure_ascii=False)
        
    print(f"🎉 URLs actualizadas: {updated_count}/{len(queue)}")

if __name__ == "__main__":
    fix_urls()
