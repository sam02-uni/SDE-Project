from fastapi import FastAPI, Depends
from sqlmodel import Session, select

from models import * # tutte le classi modello vengono caricate in fastapi
from database import init_db, get_session
from routers import users, leagues

app = FastAPI(title="Fanta Data Service")

app.include_router(users.router)
app.include_router(leagues.router)

@app.on_event("startup")
def on_startup():
    init_db()
    print("Database initialized and tables created!")


@app.get("/")
def read_root():  # : usare async methods se nel codice chiami terze parti con await
    return {"message": "User Data Service is running"}


