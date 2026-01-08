from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint, Column, text, TIMESTAMP # type: ignore

# TABELLE SQL

class Participant(SQLModel, table=True):  # Partecipazione di un User a una League
    user_id: int = Field(foreign_key="user.id", primary_key=True) # Foreign Key verso User
    league_id: int = Field(foreign_key="league.id", primary_key=True) # Foreign Key verso League
    '''join_date: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ))'''

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


# DATA OBJECTS (per richieste/risposte API)



