from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func, or_, delete, insert
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
        lower_name = name.lower()
        search_term = func.unaccent(lower_name)
        
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

def logica_upsert(rating: PlayerRating, session: Session):
    data = rating.model_dump()
    
    stmt = insert(PlayerRating).values(data)
    
    # Definiamo cosa fare in caso di conflitto sulle chiavi
    stmt = stmt.on_conflict_do_update(
        index_elements=['player_id', 'matchday_id'], # I campi che causano il duplicato
        set_={
            "fanta_rating": stmt.excluded.fanta_rating,
            "real_rating": stmt.excluded.real_rating,
        }
    )

    session.exec(stmt)
    session.commit()

    updated_rating = session.exec(
        select(PlayerRating).where(
            PlayerRating.player_id == rating.player_id,
            PlayerRating.matchday_id == rating.matchday_id
        )
    ).first()

    return updated_rating

# TODO: forse aggiungi un query param UPSERT logic
@router.post("/rating", response_model=PlayerRating, status_code=201) # POST /players/rating
def add_player_rating(rating: PlayerRating,  session: Session = Depends(get_session)) -> PlayerRating:
    player = session.get(Player, rating.player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    matchday = session.get(MatchDay, rating.matchday_id)
    if not matchday:
        raise HTTPException(status_code=404, detail="MatchDay not found")

    # UPSERT logic:
    #return logica_upsert(rating)
    
    # No update logic:
    try:
        with session.begin_nested():
            session.add(PlayerRating(**rating))
            session.commit()
    except Exception: # Se esiste già, passa oltre
        session.rollback()
        raise HTTPException(status_code=409, detail='Player rating alraedy exists')
    
     
    #session.add(rating)
    #session.commit()
    session.refresh(rating)
    return rating





# TODO: forse endpoint per il get di più giocatori