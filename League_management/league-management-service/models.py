from pydantic import BaseModel
import enum
from typing import Optional
class BaseLeagueModel(BaseModel):
    name: str
    max_credits: int

class PlayerPosition(str, enum.Enum):
    G = "G"
    D = "D"
    M = "M"
    A = "A"

class Player(BaseModel):
    id: int
    name: str
    surname: str 
    role: PlayerPosition
    serie_a_team: str 
    mean_rating: float 

class ParticipantUserWithSquad(BaseModel):
    email_user: str
    squad_name: str
    players: list[Player] 

class EssentialLeagueInfo(BaseModel):
    id: int
    name: str

class SquadWithPlayers(BaseModel):
    id: int
    owner_id: int
    league_id: int
    name: str
    score: float 
    players: list[Player]

class TableSquadInfo(BaseModel):
    name: str
    score: float

class InfoDashboard(BaseModel):
    isAdmin: bool
    squad: Optional[SquadWithPlayers] = None
    currentMatchday: int
    firstMatchStarted: bool
    lastMatchFinished: bool
    table: list[TableSquadInfo]

 