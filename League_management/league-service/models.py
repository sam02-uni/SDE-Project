from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class BaseLeagueModel(BaseModel):
    name: str
    max_credits: int

class EssentialLeagueInfo(BaseModel):
    id: int
    name: str
    
class emailParticipant(BaseModel):
    email_participant: str

class League(BaseModel):
    id: int
    owner_id: int 
    name: str 
    creation_date: datetime
    max_credits: int
    winner: Optional[str] = None

class TableSquadInfo(BaseModel):
    name: str
    score: float