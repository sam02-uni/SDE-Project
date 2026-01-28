import processCentric
import os
import httpx
import requests
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional

tags_metadata = [ # per la documentazione Swagger
    {
        "name": "Process_News_Service",
        "description": "Collect data for the interface",
    },
]

app = FastAPI(title="Process Centric News", openapi_tags=tags_metadata)

# Monta i file statici per il servizio
app.mount("/Static", StaticFiles(directory="Static"), name="static")

# Rende accessibile il servizio anche ai file ed alle pagine esterne
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permette a TUTTI i siti di chiamare questa API. 
    allow_credentials=True,
    allow_methods=["*"], # Permette GET, POST, ecc.
    allow_headers=["*"], # Permette tutti gli header
)

# Recupero URL necessari al servizio
TOKEN_URL = os.getenv("TOKEN_URL", "http://localhost:8000")
AGG_URL = os.getenv("AGG_URL", "http://localhost:8003")
HTML_URL = os.getenv("HTML_URL", "http://localhost:8006")

@app.get("/")
def read_root():
    """Return if the service is running or not"""
    return {"Lineup Business service is running"}

@app.get("/news")
async def takeNews(request: Request):
    """Take and return the data from RSS and HTML"""
    # Recurpero i dati per la verifica dell'accesso
    biscotto = request.cookies.get("access_token")
    if not biscotto:
        raise HTTPException(status_code=401, detail="Access token mancante")
    
    # Chiamo il servizio di verifica a livello business
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{AGG_URL}/compute",
            headers={"Authorization": f"Bearer {biscotto}"}
        )
        
    if resp.status_code == 401:
        raise HTTPException(status_code=401, detail="Token non valido")        
    
    if resp.status_code == 200:
    # Recupero delle informazioni riguardo alle news
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(f"{AGG_URL}/rss-fanta")
            RSSdata = response.json()
            rss_list = RSSdata.get("news", RSSdata) if isinstance(RSSdata, dict) else RSSdata
            response = await client.get(f"{HTML_URL}/html-fanta")
            HTMLdata = response.json()
            html_list = HTMLdata.get("news", HTMLdata) if isinstance(HTMLdata, dict) else HTMLdata
            data = processCentric.merge_and_sort_news(rss_list, html_list)
            # print (data)
            return {"Response" : data}
    else:
        raise HTTPException(status_code=resp.status_code, detail="Internal error")

@app.get("/news-filter")
async def takeFilNews(request: Request, tags: Optional[List[str]] = Query(None)):
    """Take and return the data filtered from RSS and HTML"""
    # Recurpero i dati per la verifica dell'accesso
    biscotto = request.cookies.get("access_token")
    if not biscotto:
        raise HTTPException(status_code=401, detail="Access token mancante")
    # Chiamo il servizio di verifica a livello business
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{AGG_URL}/compute",
            headers={"Authorization": f"Bearer {biscotto}"}
        )
        
    if resp.status_code == 401:
        raise HTTPException(status_code=401, detail="Token non valido")
    
    if resp.status_code == 200:
    # Recupero delle informazioni riguardo alle news
        async with httpx.AsyncClient(timeout=120.0) as client:
            params = {"tags": tags} if tags else {}
            try:
                response = await client.get(f"{AGG_URL}/filter-news", params=params, timeout=10.0)
                response.raise_for_status()
                RSSdata = response.json()
                rss_list = RSSdata.get("Filter", RSSdata) if isinstance(RSSdata, dict) else RSSdata
                response = await client.get(f"{HTML_URL}/html-filter-news", params=params, timeout=10.0)
                response.raise_for_status()
                HTMLdata = response.json()
                html_list = HTMLdata.get("Filter", HTMLdata) if isinstance(HTMLdata, dict) else HTMLdata
                data = processCentric.merge_and_sort_news(rss_list, html_list)
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
    else:
        raise HTTPException(status_code=resp.status_code, detail="Internal error")