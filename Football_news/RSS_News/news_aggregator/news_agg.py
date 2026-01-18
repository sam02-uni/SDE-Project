# Filtrare e formattare le news in modo tale che siano visibili per l'utente
from typing import List

KEYWORDS = ["infortunio", "stop", "scelte", "formazione", "voti", "ufficiale", "rientro"]

def apply_fanta_filter(news_list: List[dict], active_tags: List[str] = None) -> List[dict]:
    """
    Filtra le news in base ai tag selezionati. 
    Se active_tags è None o vuoto, usa tutte le KEYWORDS.
    """
    relevant_news = []
    
    # Se l'utente non ha selezionato tag specifici, usiamo il set completo
    tags_to_check = active_tags if active_tags else KEYWORDS
    
    for item in news_list:
        # Recuperiamo titolo e riassunto (gestendo eventuali None)
        titolo = (item.get('titolo') or "").lower()
        riassunto = (item.get('riassunto') or "").lower()
        testo_completo = f"{titolo} {riassunto}"
        
        # Verifichiamo se almeno uno dei tag è presente nel testo
        if any(tag.lower() in testo_completo for tag in tags_to_check):
            relevant_news.append(item)
            
    return relevant_news

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