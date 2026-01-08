# endpoint per gli utenti

from fastapi import APIRouter, Depends, HTTPException 
from sqlmodel import Session, select
from database import get_session
from models import Participant, User, League

router = APIRouter(
    prefix="/users",     # Tutte le rotte in questo file inizieranno con /users
    tags=["Users"]       # Utile per organizzare la documentazione Swagger
)

@router.get("/", response_model=list[User])  # GET /users
def get_all_users(session: Session = Depends(get_session)) -> list[User]:
        statement = select(User)
        results = session.exec(statement).all()
        return results

@router.get("/{user_id}", response_model=User) 
def get_user(user_id: int, session: Session = Depends(get_session)) -> User:
    statement = select(User).where(User.id == user_id)
    result = session.exec(statement)
    user = result.first()
    

@router.post("/", response_model=User) # POST /users
def create_user(user: User, session: Session = Depends(get_session)) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.patch("/{user_id}", response_model=User)  # PATCH /users/{user_id}
def update_user(user_id: int, updated_user: User, session: Session = Depends(get_session)) -> User:
    db_user = session.get(User, user_id)
    if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
    user_data = updated_user.model_dump(exclude_unset=True) # aggiorna solo i campi forniti
    db_user.sqlmodel_update(user_data) # aggiorna il modello con i nuovi dati
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.delete("/{user_id}")  # DELETE /users/{user_id}
def delete_user(user_id:int, session: Session = Depends(get_session)) -> dict:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}