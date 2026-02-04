from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
import requests
import os
from models import LineUpCreate

app = FastAPI(title = "Matchday Management Service", root_path="/process/matchday-management", summary="Service to manage MatchDay processes")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],   # QUESTO abilita OPTIONS
    allow_headers=["*"],   # QUESTO abilita Authorization
)

lineup_service_url_base = os.getenv("LINEUP_SERVICE_URL_BASE", "http://lineup-service:8000/business/lineups") 
#league_service_url_base = os.getenv("LEAGUE_SERVICE_URL_BASE", "http://league-service:8000") 
squad_service_url_base = os.getenv("SQUAD_SERVICE_URL_BASE", "http://squad-service:8000/business/squads") 


def check_auth_headers(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Access token mancante o malformato")
    
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }
    return headers

@app.get("/")
def read_root():  
    return {"message": "MatchDay Management Process Centric service is running"}

# TODO: TEST
@app.get("/squads/{squad_id}/players") # get players of a squad (when inserting line up)
def get_squad_players(squad_id: int):
    response = requests.get(f"{squad_service_url_base}/business/squads/{squad_id}/with-players")
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code, detail = "Unable to get squad players")    
    return response.json()["players"]

# TODO: TEST
@app.get("/lineups/{lineup_id}/grades")
def get_lineup_grades(lineup_id: int):
    
    # update grades locally:
    response = requests.get(f"{lineup_service_url_base}/business/lineups/update_grades")
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code, detail = response.json().get('detail', 'Unable to Update grades'))
    
    # get grades for given lineup
    response =  requests.get(f"{lineup_service_url_base}/business/lineups/{lineup_id}/grades")
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code, detail = "Unable to get grades")
    return response.json()

@app.get("lineups/calculate_scores") # calcuate scores for all lineups and update in back
def calculate_scores(): 
    # TODO: decidere cosa far passare qui da GuI
    # 1: league_id (ce l'ha) e matchday (ce l'ha)
    # 2: (scelta più service oriented) una serie di id di lineups che la gui deve avere
    
    # Poi chiamare il lineup business con {lineup_id}/calculate_score per ognuna e returna per ogni linuep_id lo score alla gui
    lineup_ids = [] # fake TODO
    scores = []
    for lineup_id in lineup_ids:
        response = requests.get(f"{lineup_service_url_base}/business/lineups/{lineup_id}/calculate_score")
        if response.status_code != 200:
            raise HTTPException(status_code = response.status_code, detail = "Unable to calculate score for a lineup")
        scores.append({'lineup_id': lineup_id, 'score': scores})
    
    return scores


@app.post("/lineups", status_code=201)
def create_lineup(lineup: LineUpCreate, request: Request):

    headers = check_auth_headers(request)
    response = requests.post(f"{lineup_service_url_base}", json=jsonable_encoder(lineup), headers=headers)
    if response.status_code != 201:
        raise HTTPException(status_code = response.status_code, detail = "Not able to insert lineup")
    
    return response.json()
    

@app.get("/{squad_id}/last_score")
def get_last_score_of_squad():
    # TODO: magari quando l'utente sulla home vuole vedere ultimo risultato
    pass


