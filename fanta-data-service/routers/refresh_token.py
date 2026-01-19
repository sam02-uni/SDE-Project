from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from database import get_session
from models import RefreshToken, RefreshTokenBase, RefreshTokenStop

router = APIRouter(prefix="/refresh", tags=["Refresh token"])

@router.post("/save")
def save_refresh_token(
    data: RefreshTokenBase, 
    session: Session = Depends(get_session)
):
    # Rimuoviamo eventuali vecchi token per lo stesso utente
    statement = select(RefreshToken).where(RefreshToken.user_id == data.user_id)
    existing_tokens = session.exec(statement).all()
    for t in existing_tokens:
        session.delete(t)
    
    # Creiamo l'oggetto da salvare 
    db_token = RefreshToken.model_validate(data) 
    
    session.add(db_token)
    session.commit()
    return {"status": "success"}

@router.post("/revoke")
def revoke_refresh_token(
    data: RefreshTokenStop, 
    session: Session = Depends(get_session)
):
    statement = select(RefreshToken).where(RefreshToken.token == data.token)
    token_obj = session.exec(statement).first()
    
    if token_obj:
        session.delete(token_obj)
        session.commit()
        return {"status": "revoked"}
    
    return {"status": "already_absent"}

@router.get("/get")
def get_refresh_token(
    data: RefreshTokenStop,
    session: Session = Depends(get_session)
    ):
    
    statement = select(RefreshToken).where(RefreshToken.token == data.token)
    token_obj = session.exec(statement).first()
    return token_obj