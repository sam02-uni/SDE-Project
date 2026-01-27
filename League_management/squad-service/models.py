# Qui i modelli Response e Request dei vari endpoint

from pydantic import BaseModel

class Player(BaseModel):
    id: int 
    name: str
    surname: str 
    role: str # G,D,M,A
    serie_a_team: str 
    mean_rating: float
    
class SquadCreate(BaseModel):
    owner_email: str
    league_id: int
    name: str
    players: list[Player]