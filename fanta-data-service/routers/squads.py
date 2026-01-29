from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import SquadUpdate, Squad, SquadWithPlayers, Player

router = APIRouter(
    prefix="/squads",     # Tutte le rotte in questo file inizieranno con /squads
    tags=["Squads"]       # Utile per organizzare la documentazione Swagger
)

@router.get("/", response_model=list[Squad])  # GET /squads optional filter league_id
def get_all_squads(league_id: Optional[int] = None,session: Session = Depends(get_session)) -> list[Squad]:
    if league_id: # as query parameter filter
        result = session.exec(select(Squad).where(Squad.league_id == league_id)).all()
        return result
    else:
        result = session.exec(select(Squad)).all()
        return result
    
@router.get("/{squad_id}", response_model=Squad) # GET /squads/{squad_id} 
def get_squad_by_id(squad_id: int, session: Session = Depends(get_session)):
    squad_db = session.get(Squad, squad_id)
    if not squad_db:
        raise HTTPException(status_code = 404, detail = "Squad not found")
    
    return squad_db

@router.get("/{squad_id}/with-players", response_model= SquadWithPlayers) # GET /squads/{squad_id} with-players
def get_squad_by_id(squad_id: int,  session: Session = Depends(get_session)):
    squad_db = session.get(Squad, squad_id)
    if not squad_db:
        raise HTTPException(status_code = 404, detail = "Squad not found")
    
    return squad_db

@router.post("/", response_model=Squad, status_code=201)  # POST /squads without players list
def create_squad(squad: Squad, session: Session = Depends(get_session)) -> Squad:
    session.add(squad)
    session.commit()
    session.refresh(squad)
    return squad

@router.post("/with_players", response_model=SquadWithPlayers, status_code=201)  # POST /squads/with_players with players list
def create_squad_with_players(squad: SquadWithPlayers, session: Session = Depends(get_session)) -> SquadWithPlayers:
    new_squad = Squad(
        owner_id=squad.owner_id,
        league_id=squad.league_id,
        name=squad.name,
        score=squad.score
    )

    # 1. Prendi tutti gli ID dal JSON
    player_ids = [p.id for p in squad.players]

    # 2. Fai una sola chiamata al DB per prendere tutti i giocatori validi
    statement = select(Player).where(Player.id.in_(player_ids))
    valid_players = session.exec(statement).all()

    # 3. Li aggiungi alla squadra
    new_squad.players = valid_players

    session.add(new_squad)
    session.commit()
    session.refresh(new_squad)

    return new_squad





@router.patch("/{squad_id}", response_model=Squad)  # PATCH /squads/{squad_id} , name and score are the only modifiable attributes
def update_squad(squad_id: int, updated_squad: SquadUpdate, add_score: Optional[bool] = None, session: Session = Depends(get_session)) -> Squad:
    db_squad = session.get(Squad, squad_id)
    if not db_squad:
            raise HTTPException(status_code=404, detail="Squad not found")
    if add_score :
        if updated_squad.score is None:
            raise HTTPException(status_code=400, detail="Score to add must be provided")
        db_squad.score += updated_squad.score
        if updated_squad.name is not None:
            db_squad.name = updated_squad.name
    else:
        squad_data = updated_squad.model_dump(exclude_unset=True)
        db_squad.sqlmodel_update(squad_data)

    session.add(db_squad)
    session.commit()
    session.refresh(db_squad)
    return db_squad

@router.delete("/{squad_id}")
def delete_squad(squad_id: int, session: Session = Depends(get_session)) -> dict:
    squad_db = session.get(Squad, squad_id)
    if not squad_db:
         raise HTTPException(status_code=404, detail="Squad Not found")
    session.delete(squad_db)
    session.commit()
    return {"ok":True}

