from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint, Column, text, TIMESTAMP, JSON # type: ignore
import enum

# TABELLE SQL

class PlayerPosition(str, enum.Enum):
    G = "G"
    D = "D"
    M = "M"
    A = "A"

class Participant(SQLModel, table=True):  # Partecipazione di un User a una League
    user_id: int = Field(foreign_key="user.id", primary_key=True, ondelete="CASCADE") # Foreign Key verso User
    league_id: int = Field(foreign_key="league.id", primary_key=True, ondelete="CASCADE") # Foreign Key verso League

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)

    # python 
    leagues: list["League"] = Relationship(back_populates="participants", link_model=Participant)  # da python con User accedo alle Leghe a cui partecipa
    # NOTA: qui le virgolette servono per riferirsi a League che è definita dopo, mentre in link_model non si usano le virgolette

class League(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("owner_id", "name", "creation_date",name="unique_league_constraint"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id") # Foreign Key verso User
    name: str = Field(index=True)
    creation_date: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ))
    max_credits: int = Field(default=500)
    winner: Optional[str] = Field(default=None)

    # comodità in Python
    participants: list[User] = Relationship(back_populates="leagues", link_model=Participant)  # da python con League accedo agli User partecipanti
    owner: User = Relationship()
    squads: list["Squad"] = Relationship(back_populates="league", cascade_delete=True)  # da python con League accedo alle Rose nella lega

class PlayerSquadLink(SQLModel, table=True):
    player_id: int = Field(foreign_key="player.id", primary_key=True, ondelete="RESTRICT") # do not delete player before delete this
    squad_id: int = Field(foreign_key="squad.id", primary_key=True, ondelete="CASCADE") # delete this if squad is deleted

class Squad(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("owner_id", "league_id", name="unique_squad_constraint"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id", ondelete="CASCADE") # Foreign Key verso User
    league_id: int = Field(foreign_key="league.id", ondelete="CASCADE") # Foreign Key verso
    name: str = Field(index=True)
    score: int = Field(default=0)

    # comodità
    owner: User = Relationship() # user che possiede la rosa
    league: League = Relationship(back_populates="squads") # lega a cui appartiene la rosa
    players: list["Player"] | None = Relationship(link_model=PlayerSquadLink)  # giocatori nella rosa
    lineups: list["LineUp"] | None = Relationship(back_populates="squad", cascade_delete=True) # da squad accedo alle formazioni

class Player(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    surname: str = Field(index=True)
    role: PlayerPosition
    serie_a_team: str 
    mean_rating: float = 0.0

class MatchDay(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    year: str 
    number: int

class MatchdayStatus(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    matchday_id: int = Field(foreign_key="matchday.id", ondelete="CASCADE") # Foreign Key verso MatchDay
    played_so_far: int = 0
    total_matches: int = 10

class PlayerRating(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("player_id", "matchday_id", name="unique_rating_constraint"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="player.id", ondelete="CASCADE", index=True) # Foreign Key verso Player
    matchday_id: int = Field(foreign_key="matchday.id", ondelete="RESTRICT") # Foreign Key verso MatchDay
    fanta_rating: float
    real_rating: float

    # comodità
    player: Player = Relationship()
    matchday: MatchDay = Relationship()

class PlayerLineUpLink(SQLModel, table=True):
    player_id: int = Field(foreign_key="player.id", primary_key=True, ondelete="RESTRICT") # do not delete player before delete this
    lineup_id: int = Field(foreign_key="lineup.id", primary_key=True, ondelete="CASCADE") # delete this if lineup is deleted
    is_starting: bool  # starting or bench  

    lineup: "LineUp" = Relationship(back_populates="players")  # no link model così otteniamo anche is_starting da lineup
    player: Player = Relationship()

class LineUp(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    squad_id: int = Field(foreign_key="squad.id", ondelete="CASCADE") # Foreign Key verso Squad
    matchday_id: int = Field(foreign_key="matchday.id", ondelete="RESTRICT") # Foreign Key verso MatchDay
    score: int = Field(default=0)

    players: list[PlayerLineUpLink] = Relationship(back_populates="lineup")
    squad: Squad = Relationship(back_populates="lineups")




# DATA OBJECTS (per richieste/risposte API)

class LeagueUpdate(SQLModel):
    name: Optional[str] = None
    max_credits: Optional[int] = None
    winner: Optional[str] = None

class SquadUpdate(SQLModel):
    name: Optional[str] = None
    score: Optional[int] = None
    
class LeagueWithParticipants(SQLModel):
    id: Optional[int] = None
    owner_id: int
    name: str
    creation_date: datetime
    max_credits: int
    winner: Optional[str]
    participants: list[User] = []
    owner : User

class SquadWithPlayers(SQLModel):
    id: Optional[int] = None
    owner_id: int
    league_id: int
    name: str
    score: int = 0
    players: list[Player] = []

class PlayerInLineUp(SQLModel):
    is_starting: bool
    player: Player

class LineUpWithPlayers(SQLModel):
    id: Optional[int] = None
    squad_id: int
    matchday_id: int
    players: list[PlayerInLineUp] = []

class LineUpUpdate(SQLModel):
    players: Optional[list[PlayerInLineUp]] = None
    score: Optional[int] = None

class MatchDayStatusUpdate(SQLModel):
    played_so_far: int

#REFRESH TOKEN
class RefreshTokenBase(SQLModel):
    token: str
    user_id: int
    expires_at: datetime

# Questo è il modello della tabella nel Database
class RefreshToken(RefreshTokenBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

# Questo è quello che uso per il Logout e get
class RefreshTokenStop(SQLModel):
    token: str