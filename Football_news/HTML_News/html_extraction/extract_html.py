from typing import List

KEYWORDS = ["infortunio", "stop", "scelte", "formazione", "voti", "ufficiale", "rientro"]

# Function that applies the selected filters
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