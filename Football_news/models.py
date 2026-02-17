from typing import List
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class NewsItem(BaseModel):
    fonte: str
    titolo: str
    riassunto: str
    data: datetime
    link: str

class NewsResponse(BaseModel):
    news: List[NewsItem]

class FilterResponse(BaseModel):
    Filter: List[NewsItem]

class FinalResponse:
    Response: List[NewsItem]