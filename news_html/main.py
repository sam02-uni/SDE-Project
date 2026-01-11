import html_scraper
from fastapi import FastAPI

tags_metadata = [ # per la documentazione Swagger
    {
        "name": "RSS_feed",
        "description": "Retrieve data from some journals",
    },
]

app = FastAPI(title="RSS Adapter", openapi_tags=tags_metadata)
@app.on_event("startup")
def on_startup():
    data = html_scraper.fetch_fanta_news()

@app.get("/fantanews")
def get_News_Fanta():  # : usare async methods se nel codice chiami terze parti con await
    return html_scraper.fetch_fanta_news()


