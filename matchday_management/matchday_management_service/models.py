from pydantic import BaseModel
from typing import Optional

class LineUpCreate(BaseModel):
    squad_id: int 
    matchday_number: int 
    starting_ids: list[int]
    bench_ids: list[int]