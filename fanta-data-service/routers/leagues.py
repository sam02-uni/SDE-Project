# Endpoint per le leghe
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from database import get_session
#from models import League

router = APIRouter(
    prefix="/leagues",     # Tutte le rotte in questo file inizieranno con /leagues
    tags=["Leagues"]       # Utile per organizzare la documentazione Swagger
)

@router.get("/")  # GET /leagues
def get_all_leagues(session: Session = Depends(get_session)):
    #TODO
    return {"message": "TODO"}