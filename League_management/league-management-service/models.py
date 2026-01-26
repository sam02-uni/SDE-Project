from pydantic import BaseModel

class BaseLeagueModel(BaseModel):
    name: str
    max_credits: int

class Player(BaseModel):
    id: int 
    name: str
    surname: str 
    role: str # G,D,M,A
    serie_a_team: str 
    mean_rating: float

class ParticipantUserWithSquad(BaseModel):
    email_user: str
    squad_name: str
    players: list[Player] 