from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class NewsItem(BaseModel):
    fonte: str
    titolo: str
    riassunto: str
    data: datetime
    link: str