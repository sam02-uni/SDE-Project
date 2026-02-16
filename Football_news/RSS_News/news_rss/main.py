import feed_RSS
from models import *
from fastapi import FastAPI

tags_metadata = [ # per la documentazione Swagger
    {
        "name": "RSS_feed",
        "description": "Retrieve data from some journals",
    },
]

app = FastAPI(title="RSS Adapter", openapi_tags=tags_metadata)

@app.get("/fantanews", response_model = NewsItem, summary = "Retrieve the data from the RSS file")
def get_News_Fanta():  # : usare async methods se nel codice chiami terze parti con await
    """Method that return the JSON from the RSS file of a journal"""
    return feed_RSS.fetch_fanta_news()


