# Filtrare e formattare le news in modo tale che siano visibili per l'utente

def rss_filter(news):
    filtered_news = []
    
    for item in news:
        notizia = item.get('notizia', {}) 

        new_item = {
            'titolo': notizia.get('title', 'Titolo non disponibile'),
            'riassunto': notizia.get('summary', {}).get('value', 'Nessun riassunto') if isinstance(notizia.get('summary'), dict) else notizia.get('summary', 'Nessun riassunto'),
            'link': notizia.get('link', '#'),
            'data': notizia.get('published', 'N/A'),
            'fonte': item.get('fonte', 'Sconosciuta')
        }
        filtered_news.append(new_item)

    return filtered_news