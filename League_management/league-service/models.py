from pydantic import BaseModel


class BaseLeagueModel(BaseModel):
    name: str
    max_credits: int