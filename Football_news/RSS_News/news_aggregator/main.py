import news_agg
import os
import httpx
from fastapi import FastAPI, Query, Depends
from typing import List, Optional
from dependency import verify_token

tags_metadata = [ # per la documentazione Swagger
    {
        "name": "News_Aggregator",
        "description": "Retrieve data from some journals",
    },
]

app = FastAPI(title="RSS Aggregator", openapi_tags=tags_metadata)

# Prende gli URL dei servizi necessari al funzionamento
RSS_URL = os.getenv("RSS_URL", "http://localhost:8002")

@app.get("/rss-fanta")
async def call_RSS():
    """Method that take and return the data needed for the news section"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{RSS_URL}/fantanews")
        data = response.json() 
        filtered_response = news_agg.rss_filter(data)
        return {"news": filtered_response}
    
@app.get("/filter-news")
async def get_filtered_news(tags: Optional[List[str]] = Query(None)):
    """Take the filtered news"""
    async with httpx.AsyncClient() as client:
        news_list = await call_RSS() 
        data = news_list.get("news", []) 
        filtered_data = news_agg.apply_fanta_filter(data, tags)
        return {"Filter": filtered_data}
    
@app.get("/compute")
async def compute(user: dict = Depends(verify_token)):
    """Verify token"""
    user_id = user["user_id"]
    return {"user_id": user_id, "message": "Business logic eseguita correttamente"}