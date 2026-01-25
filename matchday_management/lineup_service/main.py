from fastapi import FastAPI
import requests
import os
from models import BaseLineUp

app = FastAPI(title= "lineup business service", root_path="/business/lineup")
grades_scraper_service_url_base = os.getenv("GRADES_SCRAPER_URL_BASE", "http://grades-scraper-service:8000")
data_service_url_base = os.getenv("DATA_SERVICE_URL_BASE", "http://data-service:8000")


@app.get("/")
def read_root():
    return {"Lineup Business service is running"}

@app.post("/")
def insert_lineup(base_line_up: BaseLineUp):
    # TODO: trova id user corrente
    # TODO: trova squad_id di user corrente nella lega se squad_id non presente in base_line_up
    # TODO: controlli numero giocatori e matchday
    pass
    

# nell'endpoint get_voti prima controlli sul db e poi se non ci sono li prendi da scraper e salvi e returni
@app.get("/update_grades")
def update_grades():
    response = requests.get(f"{grades_scraper_service_url_base}/scrape_grades/22")
    players = response.json()
    matchday = players['matchday']
    players = players['grades']

    # associazione dei nomi
    for player in players:
        response = requests.get(f"{data_service_url_base}/players?name={player['']}")


# calcolo punteggio per formazione e giocatori ?

'''
class LineUp(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    squad_id: int = Field(foreign_key="squad.id", ondelete="CASCADE") # Foreign Key verso Squad
    matchday_id: int = Field(foreign_key="matchday.id", ondelete="RESTRICT") # Foreign Key verso MatchDay
    starting_players: list[str] = Field(sa_column=Column(JSON)) # lista di cognomi
    bench_players: list[str] = Field(sa_column=Column(JSON))

    squad: Squad = Relationship(back_populates="lineups")'''