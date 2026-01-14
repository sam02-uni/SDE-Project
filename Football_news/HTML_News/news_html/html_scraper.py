import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
from newspaper import Article

# URL e il tag HTML
SOURCES = {
    "SOS Fanta": "https://www.sosfanta.com/news-formazioni/",
    "Gazzetta": "https://www.gazzetta.it/calcio/serie-a/"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}

def grab_news():
    all_news = [] 
    
    for name, url in SOURCES.items():
        try:
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Cerchiamo i titoli
            titles = soup.find_all(['h2', 'h3', 'h4'], limit=10)
            
            for t in titles:
                text = t.get_text(strip=True)
                link_tag = t.find('a') or (t if t.name == 'a' else None)
                link = ""
                
                if link_tag and link_tag.has_attr('href'):
                    link = link_tag['href']
                
                # Filtro lunghezza
                if len(text) > 20:
                    # 1. Costruzione link completo
                    full_link = link
                    if link and not link.startswith('http'):
                        base_url = "https://www.gazzetta.it" if "gazzetta" in url else "https://www.sosfanta.com"
                        full_link = base_url + link

                    # 2. Estrazione Riassunto con Newspaper3k
                    riassunto = "Riassunto non disponibile."
                    if full_link.startswith('http'):
                        try:
                            # download_timeout ridotto per evitare blocchi infiniti
                            article = Article(full_link, language='it', request_timeout=5)
                            article.download()
                            article.parse()
                            # Prendiamo i primi 200 caratteri e puliamo i ritorni a capo
                            if article.text:
                                riassunto = " ".join(article.text[:200].split()) + "..."
                        except Exception as e:
                            print(f"Errore scraping articolo {full_link}: {e}")

                    # 3. Costruzione oggetto finale
                    all_news.append({
                        "sorgente": name,
                        "titolo": text,
                        "riassunto": riassunto, # Nuovo campo aggiunto
                        "link": full_link,
                        "categoria": "Fantacalcio"
                    })

        except Exception as e:
            print(f"Errore su {name}: {e}")

    return json.dumps(all_news, indent=4, ensure_ascii=False)

# Esecuzione
#risultato_json = grab_news()
#print(risultato_json)

