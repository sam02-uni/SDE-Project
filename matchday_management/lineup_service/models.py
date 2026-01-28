from pydantic import BaseModel
from typing import Optional

class LineUpCreate(BaseModel):
    league_id: Optional[int] = None # se non passa squad lega è obbligatorio
    squad_id: Optional[int] = None # se passa squad ho anche lega
    matchday_id: int # TODO: vedi se cambiar con matchday come stringa ex '22'
    starting_ids: list[int]
    bench_ids: list[int]