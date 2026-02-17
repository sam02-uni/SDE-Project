from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class NewsItem:
    fonte: str
    notizia: List[Dict[str, Any]]