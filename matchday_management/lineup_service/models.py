from pydantic import BaseModel
from typing import Optional
import enum

class LineUp(BaseModel):
    id: int
    squad_id: int 
    matchday_id: int 
    score: float 

class LineUpCreate(BaseModel):
    league_id: Optional[int] = None # se non passa squad lega è obbligatorio
    squad_id: Optional[int] = None # se passa squad ho anche lega
    matchday_number: int 
    starting_ids: list[int]
    bench_ids: list[int]

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

class PlayerGrade(BaseModel):
    is_starting: bool
    player: Player
    real_rating: Optional[float]
    fanta_rating: Optional[float]

class LineUpScore(BaseModel):
    score_lineup: float

class PlayerInLineUp(BaseModel):
    is_starting: bool
    player: Player

class LineUpWithPlayers(BaseModel):
    id: Optional[int] = None
    squad_id: int
    matchday_id: int
    score: Optional[float] = 0.0
    players: list[PlayerInLineUp] = []