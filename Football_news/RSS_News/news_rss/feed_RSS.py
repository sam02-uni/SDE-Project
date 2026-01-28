import feedparser

# Lista dei feed RSS
FEED_URLS = [
    "https://www.corrieredellosport.it/rss/calcio/serie-a",
    "https://www.tuttosport.com/rss/calcio/serie-a"
    #"https://www.calciomercato.com/feed",
    # "https://www.fantacalcio.it/rss"
]

def fetch_fanta_news():
    """Take the news from some site. Published the link of the news"""
    rss_feed = []

    for url in FEED_URLS:
        feed = feedparser.parse(url)
        
        for entry in feed.entries:
            news_item = {
                'fonte': feed.feed.title,
                'notizia': entry
            }
            rss_feed.append(news_item)
    
    return rss_feed
