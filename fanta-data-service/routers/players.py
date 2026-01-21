from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from database import get_session
from models import Player
from typing import Optional


router = APIRouter(
    prefix="/players",
    tags=["Players"]
)

# Players Endpoints

@router.get("/{player_id}", response_model=Player) # GET /players/{player_id}
def get_player(player_id: int, session: Session = Depends(get_session)) -> Player:
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@router.get("/", response_model=list[Player])
def get_players(name:Optional[str] = None, session: Session = Depends(get_session)) -> list[Player]: # name query param not mandatory
    if name:
        statement = select(Player).where(
            func.lower(Player.surname).contains(name.lower())
        )
        players = session.exec(statement).all()
        return players
    else:
        return session.exec(select(Player)).all()

@router.post("/", response_model=Player) # POST /players
def create_player(player: Player, session: Session = Depends(get_session)) -> Player:
    session.add(player)
    session.commit()
    session.refresh(player)
    return player

@router.post("/chunk", status_code=201) # POST /players/chunk
def create_players_chunk(players: list[Player], session: Session = Depends(get_session)):
    for player in players:
        session.add(player)
    session.commit()
    return {"ok": True}

@router.delete("/{player_id}")  # DELETE /players/{player_id}
def delete_player(player_id:int, session: Session = Depends(get_session)):
    player = session.get(Player, player_id)  
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    session.delete(player)
    session.commit()
    return {"ok": True}