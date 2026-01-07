from fastapi import FastAPI, Depends
from sqlmodel import Session, select

from models import User
from database import init_db, get_session


app = FastAPI(title="User Data Service")

@app.on_event("startup")
def on_startup():
    init_db()
    print("Database inizializzato e tabelle create!")


@app.get("/")
def read_root():  # TODO: usare async methods se nel codice chiami terze parti con await
    return {"message": "User Data Service is running"}

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    # Qui andrà la logica per leggere dal DB
    return {"id": user_id, "username": "FantaPlayer1", "credits": 500}

@app.get("/users/")
def get_all_users(session: Session = Depends(get_session)) -> list[User]:
        statement = select(User)
        results = session.exec(statement).all()
        return results