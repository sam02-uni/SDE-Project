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
@app.on_event("startup")
def on_startup():
    call_b()

RSS_URL = os.getenv("RSS_URL", "http://localhost:8002")

@app.get("/rss-fanta")
async def call_b():
    async with httpx.AsyncClient() as client:
        # Qui service_a contatta service_b usando il DNS interno di Docker
        response = await client.get(f"{RSS_URL}/fantanews")
        return {"risposta_da_RSS": response.json()}
