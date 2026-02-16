from datetime import datetime
from dateutil import parser

# Merge response from the different sources and sort
def merge_and_sort_news(json_data1, json_data2):
    """Merge and sort news lists"""
    combined_list = (json_data1 or []) + (json_data2 or [])
    
    def get_date(x):
        d = x.get('data')
        if not d or d == 'N/A':
            return datetime.min
        try:
            parsed_date = parser.parse(d, dayfirst=True)
            return parsed_date.replace(tzinfo=None)
            
        except Exception as e:
            return datetime.min
        
    combined_list.sort(key=get_date, reverse=True)
    
    return combined_list