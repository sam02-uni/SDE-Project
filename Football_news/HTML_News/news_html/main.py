import html_scraper
from fastapi import FastAPI

tags_metadata = [ # per la documentazione Swagger
    {
        "name": "HTML_Scraper",
        "description": "Retrieve data from some journals",
    },
]

app = FastAPI(title="HTML Scaper", openapi_tags=tags_metadata)
@app.on_event("startup")
def on_startup():
    data = html_scraper.grab_news()

@app.get("/newshtml")
def get_News_Fanta():  # : usare async methods se nel codice chiami terze parti con await
    """Return a JSON with all the info necessary for the news section"""
    return html_scraper.grab_news()


