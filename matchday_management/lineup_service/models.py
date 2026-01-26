from pydantic import BaseModel
from typing import Optional

class BaseLineUp(BaseModel):
    league_id: Optional[int] = None # se non passa squad lega è obbligatorio
    squad_id: Optional[int] = None # se passa squad ho anche lega
    matchday_id: int # TODO: vedi se cambiar con matchday come stringa ex '22'
    starting: list[str]
    bench: list[str]