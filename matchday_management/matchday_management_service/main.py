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
    allow_methods=["*"],  
    allow_headers=["*"],   
)

lineup_service_url_base = os.getenv("LINEUP_SERVICE_URL_BASE", "http://lineup-service:8000/business/lineups") 
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

@app.get("/lineups/{lineup_id}/grades", summary = "get the most recent grades available for the given lineup")
def get_lineup_grades(lineup_id: int):
    
    # get lineup: 
    response = requests.get(f"{lineup_service_url_base}/{lineup_id}")
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code, detail = response.json().get('detail', 'Unable to get Lineup'))
    lineup = response.json()

    # update grades locally:
    response = requests.get(f"{lineup_service_url_base}/update_grades?matchday_id={lineup['matchday_id']}")
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code, detail = response.json().get('detail', 'Unable to Update grades'))
    
    # get grades for given lineup
    response =  requests.get(f"{lineup_service_url_base}/{lineup_id}/grades")
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code, detail = "Unable to get grades")
    return response.json()

# chiamato questo metodo aggiorna per ottenere nuova classifica dal backend
@app.get("/leagues/{league_id}/lineups/calculate_scores", summary = "calculate the scores for all the linups of the league for the given matchday") 
def calculate_scores(league_id: int, matchday_number: int, request: Request): 
    
    headers = check_auth_headers(request)

    # get squads of the league
    response = requests.get(f"{squad_service_url_base}/by-league?league_id={league_id}")
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code, detail = response.json()['detail'])
    squads = response.json()

    # get lineups for given matchday and calculate
    scores = [] 
    for squad in squads:
        print(f"sto valutando i voti della formazione del matchday numero {matchday_number} per la squadra {squad['name']}")
        response = requests.get(f"{lineup_service_url_base}/by-squad?squad_id={squad['id']}&matchday_number={matchday_number}")
        if response.status_code != 200:
            raise HTTPException(status_code = response.status_code, detail = response.json()['detail'])
        lineup_for_matchday = response.json()[0]

        print("la lineup ha id:", lineup_for_matchday)
        # calculate:
        response = requests.get(f"{lineup_service_url_base}/{lineup_for_matchday['id']}/calculate_score", headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code = response.status_code, detail = "Unable to calculate score for a lineup")
        score_lineup = response.json()

        scores.append({'lineup_id': lineup_for_matchday['id'], 'score': score_lineup['score_lineup']})

    return scores # Servono ? 


@app.post("/lineups", status_code=201, summary="It deals with the lineup insertion")
def create_lineup(lineup: LineUpCreate, request: Request):

    headers = check_auth_headers(request)
    response = requests.post(f"{lineup_service_url_base}", json=jsonable_encoder(lineup), headers=headers)
    if response.status_code != 201:
        raise HTTPException(status_code = response.status_code, detail = "Not able to insert lineup")
    
    return response.json()

@app.patch("/lineups")
def modify_lineup(lineup: LineUpCreate, request: Request):
    # TODO, SERVE ?
    pass
    

@app.get("/{squad_id}/last_score")
def get_last_score_of_squad():
    # TODO , SERVE ? 
    pass

# TODO: delete ?


