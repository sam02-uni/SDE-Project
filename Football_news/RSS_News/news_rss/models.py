import List
import Dict
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class NewsItem:
    fonte: str
    notizia: List[Dict[str, Any]]