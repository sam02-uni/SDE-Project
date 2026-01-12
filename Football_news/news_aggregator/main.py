import news_agg
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
    data = feed_RSS.fetch_fanta_news()

@app.get("/fantanews")
def get_News_Fanta():  # : usare async methods se nel codice chiami terze parti con await
    return feed_RSS.fetch_fanta_news()


