from fastapi import FastAPI, HTTPException
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
# @app.get("/get_grades")


@app.get("/update_grades")
def update_grades():
    response = requests.get(f"{grades_scraper_service_url_base}/scrape_grades/22")
    players_scraped = response.json()

    matchday = players_scraped['matchday']
    response = requests.get(f"{data_service_url_base}/matchdays?matchday_number={matchday}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Matchday not found")
    matchday_db_id = response.json()[0]['id']

    players_scraped = players_scraped['grades']   # squad_name, player_surname, grade, fanta_grade

    # associazione dei nomi
    for player_scraped in players_scraped:
        response = requests.get(f"{data_service_url_base}/players?name={player_scraped['player_surname']}&serie_a_team={player_scraped['squad_name']}")
        if response.status_code != 200:
            continue # non carico voto
        players_found_db = response.json()
        if len(players_found_db) == 0:
            continue # non carico voto
        print("arrivato qui:", player_scraped['player_surname'])

        # 1 o più giocatori comunque li metto lo stesso voto a tutti
        for player_found_db in players_found_db:
            payload = dict(
                player_id=player_found_db['id'],
                matchday_id=matchday_db_id,
                real_rating=player_scraped['grade'],
                fanta_rating=player_scraped['fanta_grade']
            )
            response = requests.post(f"{data_service_url_base}/players/rating", json=payload)
            if response.status_code != 201:
                error_detail = response.json()['detail']
                raise HTTPException(status_code=response.status_code, detail=f"Grade not inserted because of: {error_detail}")
          
    return {"message": "Grades updated successfully"}
            



# calcolo punteggio per formazione e giocatori ?

'''
class LineUp(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    squad_id: int = Field(foreign_key="squad.id", ondelete="CASCADE") # Foreign Key verso Squad
    matchday_id: int = Field(foreign_key="matchday.id", ondelete="RESTRICT") # Foreign Key verso MatchDay
    starting_players: list[str] = Field(sa_column=Column(JSON)) # lista di cognomi
    bench_players: list[str] = Field(sa_column=Column(JSON))

    squad: Squad = Relationship(back_populates="lineups")'''