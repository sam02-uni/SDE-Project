from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func, or_, delete
from database import get_session
from models import Player, PlayerRating, MatchDay
from typing import Optional
#from unidecode import unidecode

router = APIRouter(
    prefix="/players",
    tags=["Players"]
)

#def normalize_name(name:str):
    # Trasforma "Luka Modrić" in "luka modric"
    #return unidecode(name).lower().strip()

# Players Endpoints

@router.get("/rating", response_model=list[PlayerRating]) # GET /players/{player_id}/rating
def get_player_rating(matchday_id:int, player_id:Optional[int] = None, session: Session = Depends(get_session)) -> list[PlayerRating]: # matchday_id query param
    statement = select(PlayerRating)
    if player_id:
        statement = statement.where(
            PlayerRating.player_id == player_id,
            PlayerRating.matchday_id == matchday_id
        )
        rating = session.exec(statement).first()
        if not rating:
            raise HTTPException(status_code=404, detail="Rating not found")
        return [rating]
    else:
        statement = statement.where(
            PlayerRating.matchday_id == matchday_id
        )
        ratings = session.exec(statement).all()
        return ratings

@router.delete("/rating")  # DELETE /players/rating All ratings
def delete_player(session: Session = Depends(get_session)): # Delete All playerRatings

    statement = delete(PlayerRating)
    session.exec(statement)
    session.commit()
    return {"ok": True}


@router.get("/{player_id}", response_model=Player) # GET /players/{player_id}
def get_player(player_id: int, session: Session = Depends(get_session)) -> Player:
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@router.get("/", response_model=list[Player]) # GET /players with name and serie_a_team query filters
def get_players(name: Optional[str] = None, serie_a_team: Optional[str] = None, session: Session = Depends(get_session)) -> list[Player]:
    statement = select(Player)
    
    if name:
        search_term = name.lower()
        
        # Creiamo la combinazione "nome cognome" e "cognome nome" e senza accenti
        full_name = func.unaccent(func.lower(Player.name + " " + Player.surname))
        reverse_name = func.unaccent(func.lower(Player.surname + " " + Player.name))

        statement = statement.where(
            or_(
                full_name.contains(search_term),
                reverse_name.contains(search_term)
            )
        )
    
    # Aggiungiamo anche un ordinamento per rendere la lista leggibile
    statement = statement.order_by(Player.serie_a_team) #TODO cambia in surname
    
    if serie_a_team:
        statement = statement.where(
            func.lower(Player.serie_a_team).contains(serie_a_team.lower())
        )
    
    results = session.exec(statement).all()
    return results

@router.post("/", response_model=Player, status_code=201) # POST /players
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

@router.post("/rating", response_model=PlayerRating, status_code=201) # POST /players/rating
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





# TODO: forse endpoint per il get di più giocatori