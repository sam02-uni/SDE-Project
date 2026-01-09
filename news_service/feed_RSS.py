import feedparser
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# Lista dei feed RSS focalizzati sulla Serie A
FEED_URLS = [
    "https://www.corrieredellosport.it/rss/calcio/serie-a",
    "https://www.tuttosport.com/rss/calcio/serie-a"
]

KEYWORDS = ["infortunio", "stop", "scelte", "formazione", "voti", "ufficiale", "rientro"]
# filtered = filter_fanta_relevance(news)
# print(f"Trovate {len(filtered)} notizie rilevanti per il Fantacalcio.")

def filter_fanta_relevance(news_list):
    """Filter for the news. Need a news list"""
    relevant_news = []
    for item in news_list:
        # Controlliamo se una delle keyword è nel titolo (case-insensitive)
        if any(key in item['titolo'].lower() for key in KEYWORDS):
            relevant_news.append(item)
    return relevant_news

def scrape_gazzetta_serie_a():
    """Take the news from Gazzetta"""
    url = "https://www.gazzetta.it/calcio/serie-a/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Cerchiamo i titoli (nella Gazzetta di solito sono dentro tag h2, h3 o classi specifiche)
        # Nota: le classi CSS possono cambiare, queste sono quelle standard
        news_list = []
        titles = soup.find_all(['h2', 'h3', 'h4'], limit=15)
        
        print("--- ULTIME NEWS SERIE A (SCRAPING) ---")
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
    else:
        print(f"Impossibile accedere al sito: Errore {response.status_code}")

def fetch_fanta_news():
    """Take the news from some site. Published the link of the news"""
    aggregated_news = []

    for url in FEED_URLS:
        feed = feedparser.parse(url)
        
        for entry in feed.entries:
            news_item = {
                'titolo': entry.title,
                'link': entry.link,
                'data': entry.published if 'published' in entry else 'N/A',
                'fonte': feed.feed.title
            }
            aggregated_news.append(news_item)
    
    return aggregated_news

# Esecuzione
scrape_gazzetta_serie_a()
news = fetch_fanta_news()
for n in news[:10]: # Vediamo le prime 5 news
    print(f"[{n['fonte']}] {n['titolo']}\n{n['link']}\n")
