# Filtrare e formattare le news in modo tale che siano visibili per l'utente
from typing import List

KEYWORDS = ["infortunio", "stop", "scelte", "formazione", "voti", "ufficiale", "rientro"]

# Filter logic
def apply_fanta_filter(news_list: List[dict], active_tags: List[str] = None) -> List[dict]:
    """Filter the news based on the tags insert, if none all the keywords are used"""
    relevant_news = []
    
    # If user doesn't select any filter we applied all of them
    tags_to_check = active_tags if active_tags else KEYWORDS
    
    for item in news_list:
        titolo = (item.get('titolo') or "").lower()
        riassunto = (item.get('riassunto') or "").lower()
        testo_completo = f"{titolo} {riassunto}"
        
        # Verify if one or more of the tag are in the text
        if any(tag.lower() in testo_completo for tag in tags_to_check):
            relevant_news.append(item)
            
    return relevant_news

# Filter the information with only the data that are useful for our application
def rss_filter(news):
    """Retrieve only the data that are relevant for our application"""
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