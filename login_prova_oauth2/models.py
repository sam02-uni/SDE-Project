from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


# Modelli database
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    name: str
    google_id: str

class RefreshToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    token: str
    expires_at: datetime 