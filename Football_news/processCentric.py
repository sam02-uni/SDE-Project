from datetime import datetime
from dateutil import parser

def merge_and_sort_news(json_data1, json_data2):
    # Uniamo le liste gestendo eventuali None
    combined_list = (json_data1 or []) + (json_data2 or [])
    
    def get_date(x):
        d = x.get('data')
        if not d or d == 'N/A':
            return datetime.min
        try:
            # 1. Parsiamo la data (dateutil capisce quasi tutto)
            parsed_date = parser.parse(d, dayfirst=True)
            
            # 2. Rimuoviamo il fuso orario se presente (rende la data "naive")
            # Questo permette il confronto tra date GMT e date locali italiane
            return parsed_date.replace(tzinfo=None)
            
        except Exception as e:
            # In caso di errore di parsing, mandiamo la notizia in fondo alla lista
            return datetime.min

    # Ora la comparazione funzionerà perché tutti gli oggetti sono dello stesso tipo
    combined_list.sort(key=get_date, reverse=True)
    
    return combined_list