import news_agg
import os
import httpx
from fastapi import FastAPI

tags_metadata = [ # per la documentazione Swagger
    {
        "name": "News_Aggregator",
        "description": "Retrieve data from some journals",
    },
]

app = FastAPI(title="RSS Aggregator", openapi_tags=tags_metadata)

RSS_URL = os.getenv("RSS_URL", "http://localhost:8002")

@app.get("/rss-fanta")
async def call_RSS():
    """Method that take and return the data needed for the news section"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{RSS_URL}/fantanews")
        data = response.json() 
        filtered_response = news_agg.rss_filter(data)
        return {"news": filtered_response}
    
@app.get("/filetered-news")
async def filteredNews(): 
    """Take the filtered news"""
    news_list = await call_RSS() 
    data = news_list.get("news", []) 
    filter_news = news_agg.filter_fanta_relevance(data)
    return {"Filter": filter_news}
