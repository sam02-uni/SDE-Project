from pydantic import BaseModel
import enum

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

class InfoDashboard(BaseModel):
    isAdmin: bool
    squad: dict
    currentMatchday: int
    firstMatchStarted: bool
    lastMatchFinished: bool
    table: list[dict]