# Endpoint per le leghe
from unittest import result
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import League, User, Participant, LeagueUpdate, LeagueWithParticipants

router = APIRouter(
    prefix="/leagues",     # Tutte le rotte in questo file inizieranno con /leagues
    tags=["Leagues"]       # Utile per organizzare la documentazione Swagger
)

# leagues: 
# Relationships in SQLModel sono lazyLoading: i dati collegati non vengono caricati automaticamente, ma solo quando vi si accede esplicitamente
# con lega.participants ad esempio

@router.get("/", response_model=list[League])  # GET /leagues
def get_all_leagues(session: Session = Depends(get_session)) -> list[League]:
    result = session.exec(select(League)).all()
    return result

@router.get("/{league_id}", response_model=League) # GET /leagues/{league_id}
def get_league(league_id: int, session: Session = Depends(get_session)) -> League:
    league = session.get(League, league_id)
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    return league

@router.post("/", response_model=League) # POST /leagues
def create_league(league: League, session: Session = Depends(get_session)):
    session.add(league)
    session.commit()
    session.refresh(league)
    return league


@router.patch("/{league_id}", response_model=League)  # PATCH /leagues/{league_id}
def update_league(league_id: int, updated_league: LeagueUpdate, session: Session = Depends(get_session)) -> League:
    db_league = session.get(League, league_id)
    if not db_league:
            raise HTTPException(status_code=404, detail="League not found")
    league_data = updated_league.model_dump(exclude_unset=True) # aggiorna solo i campi forniti
    db_league.sqlmodel_update(league_data) # aggiorna il modello con i nuovi dati
    session.add(db_league)
    session.commit()
    session.refresh(db_league)
    return db_league

@router.delete("/{league_id}")  # DELETE /leagues/{league_id}
def delete_league(league_id:int, session: Session = Depends(get_session)):
    league = session.get(League, league_id)  
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    session.delete(league)
    session.commit()
    return {"ok": True}

# participants:

@router.get("/{league_id}/participants", response_model=LeagueWithParticipants, tags=["Participants"]) # GET /leagues/{league_id}/participants
def get_league_participants(league_id: int, session: Session = Depends(get_session)) -> LeagueWithParticipants:
    league_db = session.get(League, league_id)
    if not league_db:
        raise HTTPException(status_code=404, detail="League not found")
    
    league_with_participants = LeagueWithParticipants(
        id=league_db.id,
        owner_id=league_db.owner_id,
        name=league_db.name,
        creation_date=league_db.creation_date,
        max_credits=league_db.max_credits,
        winner=league_db.winner,
        participants=league_db.participants,
        owner = league_db.owner
    )
    return league_with_participants

                                                          
@router.post("/{league_id}/participants", response_model=LeagueWithParticipants,  tags=["Participants"]) # POST /leagues/{league_id}/participants
def add_participant_to_league(league_id: int, participant_id: int, session: Session = Depends(get_session)) -> LeagueWithParticipants:
    league = session.get(League, league_id)
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    user = session.get(User, participant_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    league.participants.append(user)  # aggiungo l'utente alla lista dei partecipanti della lega tramite RELATIONSHIP
    session.add(league)
    session.commit()
    session.refresh(league)
    return league

@router.delete("/{league_id}/participants/{participant_id}",  tags=["Participants"])  # DELETE /leagues/{league_id}/participants/{participant_id}
def remove_participant(league_id: int, participant_id: int, session: Session = Depends(get_session)) -> dict:
    league = session.get(League, league_id)
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    user = session.get(User, participant_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    league.participants.remove(user)
    session.add(league)
    session.commit()
    return {"ok": True}