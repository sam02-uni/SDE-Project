from typing import List
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class NewsItem(BaseModel):
    fonte: str
    titolo: str
    riassunto: str
    data: str
    link: str

class NewsResponse(BaseModel):
    news: List[NewsItem]

class FilterResponse(BaseModel):
    Filter: List[NewsItem]

class FinalResponse(BaseModel):
    Response: List[NewsItem]