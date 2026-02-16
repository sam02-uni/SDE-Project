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

class MatchDayInfo(BaseModel):
    currentMatchday: int
    count: int
    first: str
    last: str
    played: int
    firstMatchStarted: bool
    lastMatchFinished: bool

class IsOwner(BaseModel):
    is_owner: bool

class User(BaseModel):
    id: int
    username: str
    email: str

class LeagueWithParticipants(BaseModel):
    id: int
    owner_id: int
    name: str
    creation_date: datetime
    max_credits: int
    winner: Optional[str]
    participants: list[User] = []
    owner : User