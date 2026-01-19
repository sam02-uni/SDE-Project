from pydantic import BaseModel

class BaseLeagueModel(BaseModel):
    name: str
    max_credits: int

class ParticipantUserWithSquad(BaseModel):
    email_user: str
    squad_name: str
    players_surnames: list[str] 