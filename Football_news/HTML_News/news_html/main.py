import html_scraper
from models import *
from fastapi import FastAPI

tags_metadata = [ # per la documentazione Swagger
    {
        "name": "HTML_Scraper",
        "description": "Retrieve data from some journals",
    },
]

app = FastAPI(title="HTML Scaper", openapi_tags=tags_metadata)

@app.get("/newshtml", response_model=list[NewsItem], summary = "Return the info get by the html scraper")
def get_News_Fanta():  
    """Return a JSON with all the info necessary for the news section"""
    return html_scraper.grab_news()


