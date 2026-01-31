from fastapi import FastAPI, HTTPException
import requests
import os


app = FastAPI(title = "Matchday Management Service", root_path="/process/matchday_management", summary="Service to manage MatchDay processes")
lineup_service_url_base = os.getenv("LINEUP_SERVICE_URL_BASE", "http://lineup-service:8000") # TODO add in Compose
#league_service_url_base = os.getenv("LEAGUE_SERVICE_URL_BASE", "http://league-service:8000") # TODO add in Compose
squad_service_url_base = os.getenv("SQUAD_SERVICE_URL_BASE", "http://squad-service:8000") # TODO add in Compose

@app.get("/")
def read_root():  
    return {"message": "MatchDay Management Process Centric service is running"}


# TODO: TEST
@app.get("/squad/{squad_id}/players") # get players of a squad (when inserting line up)
def get_squad_players(squad_id: int):
    response = requests.get(f"{squad_service_url_base}/business/squads/{squad_id}/with-players")
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code, detail = "Unable to get squad players")    
    return response.json()["players"]

# TODO: TEST
@app.get("/lineup/{lineup_id}/grades")
def get_lineup_grades(lineup_id: int):
    # TODO: prendere il matchday info e controllare che la giornata non sia conlusa
    # se conclusa chiamare calcualte_score in lineup service e PENSARE A COME AGGIORNARE PER LA GUI
    response =  requests.get(f"{lineup_service_url_base}/business/lineup/{lineup_id}/grades")
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code, detail = "Unable to get grades")
    return response.json()


@app.post("/lineup/", status_code=201)
def create_lineup(lineup: dict):
    # TODO
    pass

@app.get("/{squad_id}last_score")
def get_last_score_of_squad():
    # TODO: magari quando l'utente sulla home vuole vedere ultimo risultato
    pass


