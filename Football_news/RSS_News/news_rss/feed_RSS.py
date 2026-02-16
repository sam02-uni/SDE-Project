import feedparser

# List of sites where the RSS feed file is available
FEED_URLS = [
    "https://www.corrieredellosport.it/rss/calcio/serie-a",
    "https://www.tuttosport.com/rss/calcio/serie-a"
]

# Retrive the data from the RSS file
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
