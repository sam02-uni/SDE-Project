from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import User, Squad, PlayerSquadLink, Player, LineUp, LineUpWithPlayers, PlayerLineUpLink

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
        
@router.get("/with_players", response_model = list[LineUpWithPlayers]) # GET /lineups/with_players?squad_id=x&giornata_id=y
def getLineUps_with_players(squad_id: Optional[int] = None, matchDay_id: Optional[int] = None, session: Session = Depends(get_session)) -> list[LineUpWithPlayers]:
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

@router.get("/{lineup_id}", response_model=LineUpWithPlayers)  # GET /lineups/{lineup_id}
def get_lineup(lineup_id: int, session: Session = Depends(get_session)) -> LineUp:
    lineup = session.get(LineUp, lineup_id)
    if not lineup:
        raise HTTPException(status_code=404, detail="LineUp not found")
    return lineup


@router.post("/", response_model=LineUp)  # POST /lineups
def create_lineup(lineup: LineUpWithPlayers, session: Session = Depends(get_session)) -> LineUp:

    new_lineup = LineUp(
        squad_id=lineup.squad_id,
        matchday_id=lineup.matchday_id
    )
    session.add(new_lineup)
    session.flush()

    for player_in_lineup in lineup.players:
        link = PlayerLineUpLink(
            player_id=player_in_lineup.player.id,
            lineup_id=new_lineup.id,
            is_starting=player_in_lineup.is_starting
        )
        session.add(link)

    session.commit()
    session.refresh(new_lineup)
    return new_lineup

@router.delete("/{lineup_id}")  # DELETE /lineups/{lineup_id}
def delete_lineup(lineup_id: int, session: Session = Depends(get_session)) -> dict:
    lineup_db = session.get(LineUp, lineup_id)
    if not lineup_db:
         raise HTTPException(status_code=404, detail="LineUp Not found")
    session.delete(lineup_db)
    session.commit()
    return {"ok":True}

@router.patch("/{lineup_id}", response_model=LineUp)  # PATCH /lineups/{lineup_id}
def update_lineup(lineup_id: int, lineup: LineUpWithPlayers, session: Session = Depends(get_session)) -> LineUp:
    lineup_db = session.get(LineUp, lineup_id)
    if not lineup_db:
        raise HTTPException(status_code=404, detail="LineUp Not found")
    
    if lineup.score:  # score aggiornato
        lineup_db.score = lineup.score

    if lineup.players:  # cambio players formazione
        # elimina i link esistenti
        existing_links = session.exec(select(PlayerLineUpLink).where(PlayerLineUpLink.lineup_id == lineup_id)).all()
        for link in existing_links:
            session.delete(link)
        session.flush()

        # aggiungi i nuovi link
        for player_in_lineup in lineup.players:
            link = PlayerLineUpLink(
                player_id=player_in_lineup.player.id,
                lineup_id=lineup_id,
                is_starting=player_in_lineup.is_starting
            )
            session.add(link)

        session.commit()
        session.refresh(lineup_db)
        return lineup_db


