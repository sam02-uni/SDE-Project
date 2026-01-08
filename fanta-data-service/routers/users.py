# endpoint per gli utenti

from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from database import get_session
from models import Participant, User, League

router = APIRouter(
    prefix="/users",     # Tutte le rotte in questo file inizieranno con /users
    tags=["Users"]       # Utile per organizzare la documentazione Swagger
)

@router.get("/")  # GET /users
def get_all_users(session: Session = Depends(get_session)) -> list[User]:
        statement = select(User)
        results = session.exec(statement).all()
        return results

@router.get("/{user_id}", response_model=list[User])  # TODO: vedi come fare per rispondere con una VISTA dello User (non User completo)
def get_user(user_id: int, session: Session = Depends(get_session)) -> User:
    # TODO: Qui andrà la logica per leggere dal DB
    return {"id": user_id, "username": "FantaPlayer1", "credits": 500}

@router.post("/", response_model=User) # POST /users
def create_user(user: User, session: Session = Depends(get_session)) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user