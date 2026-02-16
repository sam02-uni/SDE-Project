import extract_html
import os
import httpx
from fastapi import FastAPI, Query
from models import *
from typing import List, Optional

tags_metadata = [ # per la documentazione Swagger
    {
        "name": "News_Aggregator_HTML",
        "description": "Retrieve data from some journals",
    },
]

app = FastAPI(title="HTML Aggregator", openapi_tags=tags_metadata)

# Get the URL necessary to work
SCRAPE_URL = os.getenv("SCRAPE_URL", "http://localhost:8034")

@app.get("/html-fanta", response_model=NewsResponse, summary = "Return the info get by the html scraper")
async def call_HTML():
    """Method that take and return the data needed for the news section"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.get(f"{SCRAPE_URL}/newshtml")
        data = response.json() 
        return {"news": data}
    
@app.get("/html-filter-news", response_model=FilterResponse, summary = "Return the filtered info of the html scrape")
async def get_filtered_news(tags: Optional[List[str]] = Query(None)):
    """Take and return the filtered news"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        news_list = await call_HTML() 
        data = news_list.get("news", []) 
        filtered_data = extract_html.apply_fanta_filter(data, tags)
        return {"Filter": filtered_data}