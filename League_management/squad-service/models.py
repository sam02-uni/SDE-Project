# Qui i modelli Response e Request dei vari endpoint
import enum
from pydantic import BaseModel
    
class Squad(BaseModel):
    id: int
    owner_id: int 
    league_id: int 
    name: str 
    score: float 

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

class SquadCreate(BaseModel):
    owner_email: str
    league_id: int
    name: str
    players: list[Player]

class SquadScore(BaseModel):
    matchday_number: int
    score: float | str