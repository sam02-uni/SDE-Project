import feedparser

# Lista dei feed RSS focalizzati sulla Serie A
FEED_URLS = [
    "https://www.corrieredellosport.it/rss/calcio/serie-a",
    "https://www.tuttosport.com/rss/calcio/serie-a"
    #"https://www.calciomercato.com/feed",
    # "https://www.fantacalcio.it/rss"
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
#scrape_gazzetta_serie_a()
#news = fetch_fanta_news()
#for n in news[:10000]: # Vediamo le prime 5 news
#    print(f"[{n['fonte']}] {n['titolo']}\n{n['link']}\n")
