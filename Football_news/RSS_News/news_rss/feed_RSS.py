import feedparser

# Lista dei feed RSS focalizzati sulla Serie A
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
            #aggregated_news.append(news_item)
            rss_feed.append(news_item)
    
    return rss_feed

#news = fetch_fanta_news()
#print (news[0])
#for n in news[:10000]: 
#    print(f"[{n['fonte']}] {n['titolo']}\n{n['link']}\n")

# title, 'titolo': entry.title,
# summary in particolare value
# link, quello della notizia 'link': entry.link,
# published, data di pubblicazione 'data': entry.published if 'published' in entry else 'N/A',
# 'fonte': feed.feed.title