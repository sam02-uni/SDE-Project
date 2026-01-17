import process_rss
import os
import httpx
from fastapi import FastAPI

tags_metadata = [ # per la documentazione Swagger
    {
        "name": "Process_News_Service",
        "description": "Collect data for the interface",
    },
]

app = FastAPI(title="Process Centric News", openapi_tags=tags_metadata)

# RSS_URL = os.getenv("RSS_URL", "http://localhost:8002")
AGG_URL = os.getenv("AGG_URL", "http://localhost:8003")
@app.get("/news")
async def takeNews():
    """Take the data from RSS and HTML"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{AGG_URL}/rss-fanta")
        data = response.json() 
        return {"Response":data}
    
@app.get("/news-filter")
async def takeFilterNews():
    """Take the data from RSS and HTML"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{AGG_URL}/filetered-news")
        data = response.json() 
        return {"Response":data}
