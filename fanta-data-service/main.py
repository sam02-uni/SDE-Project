from fastapi import FastAPI, Depends
from sqlmodel import Session, select

from models import * # tutte le classi modello vengono caricate in fastapi
from database import init_db, get_session
from routers import users, leagues

tags_metadata = [ # per la documentazione Swagger
    {
        "name": "users",
        "description": "Operations with users.",
    },
    {
        "name": "leagues",
        "description": "Operations with leagues.",
    },
    {
        "name":"participants",
        "description":"Operations with league participants.",
    }
]

app = FastAPI(title="Fanta Data Service", openapi_tags=tags_metadata)
app.include_router(users.router)
app.include_router(leagues.router)
# TODO: vedere quando mandare 403 Forbidden in base ai permessi , se farlo qui ??do 
@app.on_event("startup")
def on_startup():
    init_db()
    print("Database initialized and tables created!")


@app.get("/")
def read_root():  # : usare async methods se nel codice chiami terze parti con await
    return {"message": "User Data Service is running"}


