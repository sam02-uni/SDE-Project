from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import User, Squad, PlayerSquadLink, Player, LineUp

router = APIRouter(
    prefix="/lineups",     # Tutte le rotte in questo file inizieranno con /lineups
    tags=["LineUp"]       # Utile per organizzare la documentazione Swagger
)

# LineUp Endopoints

@router.get("/", response_model = list[LineUp]) # GET /lineups?squad_id=x&giornata_id=y
def getLineUps(squad_id: Optional[int] = None, matchDay_id: Optional[int] = None, session: Session = Depends(get_session)) -> list[LineUp]:
    match(squad_id, matchDay_id):
        case (None, None): # get ALL lineups in the db 
            result = session.exec(select(LineUp)).all()
            return result
        case (squad_id, None): # get lineups for a specific squad
            result = session.exec(select(LineUp).where(LineUp.squad_id == squad_id)).all()
            return result
        case (None, matchDay_id): # get lineups for a specific matchday
            result = session.exec(select(LineUp).where(LineUp.matchday_id == matchDay_id)).all()
            return result
        case (squad_id, matchDay_id): # get lineups for a specific squad and matchday
            result = session.exec(select(LineUp).where((LineUp.squad_id == squad_id) & (LineUp.matchday_id == matchDay_id))).all()
            return result
        

@router.get("/{lineup_id}", response_model=LineUp)  # GET /lineups/{lineup_id}
def get_lineup(lineup_id: int, session: Session = Depends(get_session)) -> LineUp:
    lineup = session.get(LineUp, lineup_id)
    if not lineup:
        raise HTTPException(status_code=404, detail="LineUp not found")
    return lineup


@router.post("/", response_model=LineUp)  # POST /lineups
def create_lineup(lineup: LineUp, session: Session = Depends(get_session)) -> LineUp:
    session.add(lineup)
    session.commit()
    session.refresh(lineup)
    return lineup

@router.delete("/{lineup_id}")  # DELETE /lineups/{lineup_id}
def delete_lineup(lineup_id: int, session: Session = Depends(get_session)) -> dict:
    lineup_db = session.get(LineUp, lineup_id)
    if not lineup_db:
         raise HTTPException(status_code=404, detail="LineUp Not found")
    session.delete(lineup_db)
    session.commit()
    return {"ok":True}


