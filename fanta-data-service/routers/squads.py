from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import League, SquadUpdate, User, Squad, PlayerSquadLink, Player

router = APIRouter(
    prefix="/squads",     # Tutte le rotte in questo file inizieranno con /squads
    tags=["Squads"]       # Utile per organizzare la documentazione Swagger
)

# Squads Endpoints

@router.get("/", response_model=list[Squad])  # GET /squads
def get_all_squads(league_id: Optional[int] = None,session: Session = Depends(get_session)) -> list[Squad]:
    if league_id: # as query parameter filter
        result = session.exec(select(Squad).where(Squad.league_id == league_id)).all()
        return result
    else:
        result = session.exec(select(Squad)).all()
        return result
    
@router.post("/", response_model=Squad)  # POST /squads
def create_squad(squad: Squad, session: Session = Depends(get_session)) -> Squad:
    session.add(squad)
    session.commit()
    session.refresh(squad)
    return squad

@router.patch("/{squad_id}", response_model=Squad)  # PATCH /squads/{squad_id} , name and score are the only modifiable attributes
def update_squad(squad_id: int, updated_squad: SquadUpdate, session: Session = Depends(get_session)) -> Squad:
    db_squad = session.get(Squad, squad_id)
    if not db_squad:
            raise HTTPException(status_code=404, detail="Squad not found")
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

