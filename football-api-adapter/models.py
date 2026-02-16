from pydantic import BaseModel

class PlayerAPI(BaseModel):
    id: int
    name: str
    position: str
    dateOfBirth: str
    nationality: str

class TeamAPI(BaseModel):
    name: str
    squad: list[PlayerAPI]

class MatchDayInfo(BaseModel):
    currentMatchday: int
    count: int
    first: str
    last: str
    played: int
    firstMatchStarted: bool
    lastMatchFinished: bool

class MatchAPI(BaseModel):
    utcDate: str
    homeTeam: str
    awayTeam: str
    score_homeTeam: int
    score_awayTeam: int