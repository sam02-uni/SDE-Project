import process_rss
import os
import httpx
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

tags_metadata = [ # per la documentazione Swagger
    {
        "name": "Process_News_Service",
        "description": "Collect data for the interface",
    },
]

app = FastAPI(title="Process Centric News", openapi_tags=tags_metadata)

# Rende accessibile il servizio anche ai file ed alle pagine esterne
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permette a TUTTI i siti di chiamare questa API. 
    allow_credentials=True,
    allow_methods=["*"], # Permette GET, POST, ecc.
    allow_headers=["*"], # Permette tutti gli header
)

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
async def takeFilNews(tags: Optional[List[str]] = Query(None)):
    """Take the data filtered from RSS and HTML"""
    async with httpx.AsyncClient() as client:
        params = {"tags": tags} if tags else {}
        try:
            # Invio della richiesta all'aggregatore
            response = await client.get(f"{AGG_URL}/filter-news", params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            return JSONResponse(content={"Response": data})

        except httpx.HTTPStatusError as exc:
            return JSONResponse(
                status_code=exc.response.status_code,
                content={"error": "L'aggregatore ha restituito un errore", "details": str(exc)}
            )
        except httpx.RequestError as exc:
            return JSONResponse(
                status_code=503,
                content={"error": "Aggregatore non raggiungibile", "details": str(exc)}
            )