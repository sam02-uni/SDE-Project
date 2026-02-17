from pydantic import BaseModel


class GradeFantacalcio(BaseModel):
    squad_name: str
    player_surname: str
    grade: float | None
    fanta_grade: float | None
    
class MatchdayGrades(BaseModel):
    matchday: int
    grades: list[GradeFantacalcio]