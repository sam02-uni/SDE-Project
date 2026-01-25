# Match Day Endpoints
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import MatchDay
from typing import Optional

router = APIRouter(
    prefix="/matchdays",     # Tutte le rotte in questo file inizieranno
    tags=["MatchDays"]       # Utile per organizzare la documentazione Swagger
)

@router.get("/", response_model=list[MatchDay])  # GET /matchdays
def get_all_matchdays(matchday_number: Optional[int] = None, session: Session = Depends(get_session)) -> list[MatchDay]:
    if matchday_number is not None:
        matchday = session.exec(select(MatchDay).where(MatchDay.number == matchday_number)).first()
        if not matchday:
            raise HTTPException(status_code=404, detail="MatchDay not found")
        return [matchday]
    result = session.exec(select(MatchDay)).all()
    return result

@router.get("/{matchday_id}", response_model=MatchDay)  # GET /matchdays/{matchday_id}
def get_matchday(matchday_id: int, session: Session = Depends(get_session)) -> MatchDay:
    matchday = session.get(MatchDay, matchday_id)
    if not matchday:
        raise HTTPException(status_code=404, detail="MatchDay not found")
    return matchday

@router.post("/", response_model=MatchDay)  # POST /matchdays
def create_matchday(matchday: MatchDay, session: Session = Depends(get_session)) -> MatchDay:
    session.add(matchday)
    session.commit()
    session.refresh(matchday)
    return matchday