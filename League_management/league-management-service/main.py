from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
import requests
import os
from models import BaseLeagueModel, ParticipantUserWithSquad
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI(title="League managament process centric service", root_path = "/process/league-management")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],   # QUESTO abilita OPTIONS
    allow_headers=["*"],   # QUESTO abilita Authorization
)

league_service_url_base = os.getenv("LEAGUE_SERVICE_URL_BASE", "http://league-service:8000") # league business
squad_service_url_base = os.getenv("SQUAD_SERVICE_URL_BASE", "http://squad-service:8000") # squad business


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
    return {"League management process service is Running!"}

@app.post("/init", response_model=int) # restituisce id alla gui
def init_base_league(league_info: BaseLeagueModel, request: Request):
    # crea lega con nome e max_credits inseriti dall admin nella gui

    headers = check_auth_headers(request)
    print (league_service_url_base)
    response = requests.post(f"{league_service_url_base}", json=league_info.model_dump(), headers=headers)
    
    if response.status_code != 201:
        raise HTTPException(status_code=400, detail="Not Created")
    
    return response.json() # id created league

@app.get("/allPlayers")
def get_all_players():
    response = requests.get(f"{squad_service_url_base}allPlayers")
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code, detail = response.json()['detail'])
    return response.json()

@app.post("/{league_id}/add_participant", status_code=201, response_model=int) # Add User With Their Squad to League
def add_partiticant_to_league(league_id: int, participantWithSquad: ParticipantUserWithSquad, request: Request):

    headers = check_auth_headers(request)

    body_content = {
        'email_participant': participantWithSquad.email_user
    }

    # League Business service in order to add participant to league
    response = requests.post(f"{league_service_url_base}{league_id}/participants", json=body_content, headers=headers)
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.json().get('detail'))
    print("participant added:", response.json())
    
    # Squad business per creare rosa di utente in lega
    response = requests.post(f"{squad_service_url_base}", json={
        "owner_email": participantWithSquad.email_user, 
        "league_id": league_id,
        "name": participantWithSquad.squad_name,
        "players": jsonable_encoder(participantWithSquad.players)
    }, headers=headers)
    
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail="Squad not created")

    created_squad_id = response.json()['id']
    return created_squad_id # return squad created id
    

# usato quando utente scrive nome nella casella di testo e 'cerca' e restituisce i giocatori con quei nomi
@app.get("/suggest_players")
def suggest_players(given_name:str):
    response = requests.get(f"{squad_service_url_base}/business/squads/suggest_player?wanted_name={given_name}")
    return response.json() # return json list of players (all fields)

# informazioni per la home iniziale = le leghe a cui partecipa l'utente da mettere a sinistra
@app.get("/info_webapp_home")
def get_info_webapp_home(request: Request):
    headers = check_auth_headers(request)
    response = requests.get(f"{league_service_url_base}by_user", headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Not found")
    
    return response.json() # list of leagues with essential info


@app.get("/{league_id}/info_dashboard_league")
def get_info_dashboard(league_id: int, request: Request): # return info to display on the dashboard of the league for the logged in user
    
    headers = check_auth_headers(request)

    dict_result = dict()

    # is admin ?
    response = requests.get(f"{league_service_url_base}{league_id}/logged-owner", headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="not able to get league owner infos")
    
    dict_result.update({'isAdmin': True}) if response.json()['is_owner'] else dict_result.update({'isAdmin': False})

    # squad of the logged user , has a squad ?:
    response = requests.get(f"{squad_service_url_base}take_squad/{league_id}", headers=headers)
    if response.status_code != 200:
        #raise HTTPException(status_code=response.status_code, detail="not able to get squad")
        squad_with_players = None # if no, return None
    else:
        squad_with_players = response.json() # if yes, return squad
    
    dict_result.update({'squad': squad_with_players})
     
    # current matchday:
    response = requests.get(f"{league_service_url_base}current_matchday")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="not able to get current matchday infos")

    response_dict = response.json()
    dict_result.update({'currentMatchday':response_dict['currentMatchday'], 
                        'firstMatchStarted': response_dict['firstMatchStarted'], 
                        'lastMatchFinished': response_dict['lastMatchFinished']}) # GUI controllerà questo e dovrà chiamare process centric 
                                                                                  # matchday management /calculate_score

    # standing:
    response = requests.get(f"{league_service_url_base}{league_id}/table")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="not able to get standing infos")
    
    dict_result.update({'table': response.json()})


    return dict_result

@app.get("/take_squad/{league_id}")
def get_all_players(league_id: int, request: Request):
    headers = check_auth_headers(request)
    response = requests.get(f"{squad_service_url_base}take_squad/{league_id}", headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code, detail = response.json()['detail'])
    return response.json()

# TODO: delete league ?? Modify league ??


