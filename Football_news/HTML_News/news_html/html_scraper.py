import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
from newspaper import Article

# URL and tag HTML
SOURCES = {
    "SOS Fanta": "https://www.sosfanta.com/news-formazioni/",
    "Gazzetta": "https://www.gazzetta.it/calcio/serie-a/"
}

# Header for bot control
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}

# Function for retrive the news
def grab_news():
    """Retrieve all the data needed for our application from html pages"""
    all_news = [] 
    
    for name, url in SOURCES.items():
        try:
            # Recuperiamo la pagina HTML
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
                
                # Recuperiamo tutte le informazioni necessarie all'applicazione
                if len(text) > 20:
                    full_link = link
                    if link and not link.startswith('http'):
                        base_url = "https://www.gazzetta.it" if "gazzetta" in url else "https://www.sosfanta.com"
                        full_link = base_url + link

                    riassunto = "Riassunto non disponibile."
                    if full_link.startswith('http'):
                        try:
                            article = Article(full_link, language='it', request_timeout=5)
                            article.download()
                            article.parse()
                            if article.text:
                                riassunto = " ".join(article.text[:200].split()) + "..."
                            
                            if article.publish_date:
                                data_pubblicazione = article.publish_date.strftime("%d/%m/%Y %H:%M")
                            else:
                                data_pubblicazione = "N/A"
                        except Exception as e:
                            print(f"Errore scraping articolo {full_link}: {e}")

                    # Creiamo la lista da ritornare
                    all_news.append({
                        "fonte": name,
                        "titolo": text,
                        "riassunto": riassunto,
                        "data": data_pubblicazione, 
                        "link": full_link
                    })

        except Exception as e:
            print(f"Errore su {name}: {e}")

    return all_news
