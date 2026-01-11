import requests
from datetime import datetime
from bs4 import BeautifulSoup

import requests
from bs4 import BeautifulSoup

# Dizionario con URL e il tag HTML tipico che contiene il titolo in quel sito
SOURCES = {
    "SOS Fanta": "https://www.sosfanta.com/news-formazioni/",
    "Gazzetta": "https://www.gazzetta.it/calcio/serie-a/"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}

def grab_news():
    for name, url in SOURCES.items():
        try:
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Cerchiamo i titoli (h2 e h3 sono i più comuni per le news)
            titles = soup.find_all(['h2', 'h3', 'h4'], limit=5)
            
            print(f"\n--- {name.upper()} ---")
            for t in titles:
                text = t.get_text(strip=True)
                link = ""
                if t.find('a'):
                    link = t.find('a')['href']
            
            # Filtriamo solo titoli con un minimo di lunghezza per evitare menu o pubblicità
                if len(text) > 20:
                    print(f"TITOLO: {text}")
                    print(f"LINK:   {link if link.startswith('http') else 'https://www.gazzetta.it' + link}")
                    print("-" * 30)

        except Exception as e:
            print(f"Errore su {name}: {e}")

#grab_news()