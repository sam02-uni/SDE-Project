from fastapi import FastAPI, HTTPException
import requests
import os
from models import BaseLeagueModel, Player, ParticipantUserWithSquad

app = FastAPI(title="League managament process centric service", root_path = "/process/league-management")

league_service_url_base = os.getenv("LEAGUE_SERVICE_URL_BASE", "http://league-service:8000") # league business
squad_service_url_base = os.getenv("SQUAD_SERVICE_URL_BASE", "http://squad-service:8000") # squad business

@app.get("/")
def read_root():
    return {"League management process service is Running!"}

@app.post("/init", response_model=str) # restituisce id alla gui, la gui salva id in LocalStorage
def init_base_league(league_info: BaseLeagueModel):
    # crea lega con nome e max_credits inseriti dall admin nella gui
    response = requests.post(f"{league_service_url_base}/business/leagues", json=league_info)
    if response.status_code != 201:
        raise HTTPException(status_code=400, detail="Not Created")
    
    return response.json() # id created league

# TODO: To TEST
@app.post("/{league_id}/add_participant", status_code=201, response_model=str) # Add User With Their Squad to League
def add_partiticant_to_league(league_id: int, participantWithSquad: ParticipantUserWithSquad):
    
    # ENDPOINT in Business User per verificare che email esiste in db
    #  TODO

    # League Business service in order to add participant to league
    response = requests.post(f"{league_service_url_base}/business/league/{league_id}/participants", json=participantWithSquad["email_user"])
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
    # Squad business per creare rosa di utente in lega
    response = requests.post(f"{squad_service_url_base}/business/squads", json={
        "owner_id": "TODO", # get user id from email
        "league_id": league_id,
        "name": participantWithSquad["squad_name"],
        "players": participantWithSquad["players"]
    })
    
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail="Squad not created")

    return response.json() # return squad created 
    

# usato quando utente scrive nome nella casella di testo e 'cerca' e restituisce i giocatori con quei nomi
@app.get("/suggest_players")
def suggest_players(given_name:str):
    response = requests.get(f"{squad_service_url_base}/business/squads/suggest_player?wanted_name={given_name}")
    return response.json() # return json list of players (all fields)

# TODO: TEST
@app.get("/{league_id}/info_dashboard")
def get_info_dashboard(league_id: int): # return info to display on the dashboard of the league
    dict_result = dict()
    # admin ?
    # TODO

    # current matchday:
    response = requests.get(f"{league_service_url_base}/business/leaguescurrent_matchday")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="not able to get current matchday infos")

    response_dict = response.json()
    dict_result.update({'currentMatchday':response_dict['currentMatchday'], 'firstMatchStarted': response_dict['firstMatchStarted']})

    # squad of the user
    # TODO

    # standing:
    response = requests.get(f"{league_service_url_base}/business/leagues/{league_id}/table")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="not able to get standing infos")
    
    dict_result.update({'standing': response.json()})