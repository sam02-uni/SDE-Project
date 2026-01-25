from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func, or_
from database import get_session
from models import Player, PlayerRating, MatchDay
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
def get_players(name: Optional[str] = None, session: Session = Depends(get_session)) -> list[Player]:
    statement = select(Player)
    
    if name:
        search_term = name.lower()
        
        # Creiamo la combinazione "nome cognome" e "cognome nome"
        full_name = func.lower(Player.name + " " + Player.surname)
        reverse_name = func.lower(Player.surname + " " + Player.name)
        
        statement = statement.where(
            or_(
                full_name.contains(search_term),
                reverse_name.contains(search_term)
            )
        )
    
    # Aggiungiamo anche un ordinamento per rendere la lista leggibile
    statement = statement.order_by(Player.surname)
    
    results = session.exec(statement).all()
    return results

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

# players ratings endpoints
# voti presi solo a fine partita quindi non cambiano, quindi no patch/put

@router.post("/rating", response_model=PlayerRating) # POST /players/{player_id}/rating
def add_player_rating(rating: PlayerRating,  session: Session = Depends(get_session)) -> PlayerRating:
    player = session.get(Player, rating.player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    matchday = session.get(MatchDay, rating.matchday_id)
    if not matchday:
        raise HTTPException(status_code=404, detail="MatchDay not found")
    
    session.add(rating)
    session.commit()
    session.refresh(rating)
    return rating

@router.get("/{player_id}/rating", response_model=PlayerRating) # GET /players/{player_id}/rating
def get_player_rating(player_id:int, matchday_id:int, session: Session = Depends(get_session)) -> PlayerRating: # matchday_id query param
    statement = select(PlayerRating).where(
        PlayerRating.player_id == player_id,
        PlayerRating.matchday_id == matchday_id
    )
    rating = session.exec(statement).first()
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    return rating

# TODO: forse endpoint per il get di più giocatori