from fastapi import FastAPI, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
import requests
import os
from models import *
from dependency import verify_token
from typing import Optional

app = FastAPI(title="Squad Business service", root_path = "/business/squads")
data_service_url_base = os.getenv("DATA_SERVICE_URL_BASE", "http://data-service:8000")

@app.get("/")
def read_root():
    return {"squad business service is running"}

@app.post("/", status_code=201, summary = "Create a squad with the logged user as owner in the given league") 
def create_squad(info: SquadCreate, logged_user : dict = Depends(verify_token)):
    
    user_id = logged_user['user_id']
    # minimum number of players check
    players = info.players
    '''g, d, m, a = 0,0,0,0
    for player in players:
        match player.role:
            case "G":
                g+=1
                continue
            case "D":
                d+=1
                continue
            case "M":
                m+=1
                continue
            case "A":
                a+=1
                continue

    if g < 3 or d < 8 or m < 8 or a < 6: # 25 giocatori
        raise HTTPException(status_code = 400, detail="Not enough players in squad")'''
    
    # authorization : user loggato è admin della lega ?
    response = requests.get(f"{data_service_url_base}/leagues/{info.league_id}")
    if response.status_code != 200:
        raise HTTPException(status_code = 400, detail="Bad Request: the squad league does not exists")
    if user_id != response.json()['owner_id']:
        raise HTTPException(status_code = 403, detail="Action is Forbidden for the logged user")
    

    response = requests.get(f"{data_service_url_base}/users/by-email?user_email={info.owner_email}") # id dell owner della squadra
    if response.status_code != 200:
        raise HTTPException(status_code = 404, detail="Owner user not found")
    
    info_to_add = {
        "owner_id": response.json()["id"],
        "league_id": info.league_id,
        "name": info.name,
        "players": jsonable_encoder(info.players)
    }

    # call data service to create squad
    response = requests.post(f"{data_service_url_base}/squads/with_players", json=info_to_add)
    if response.status_code != 201:
        raise HTTPException(status_code = response.status_code, detail=response.text)
    
    return response.json()
    

@app.get("/suggest_player", summary = "Get the players having the given name within", response_model = list[Player]) 
def get_suggested_players(wanted_name: str): # wanted_name: query param
    if wanted_name is None or len(wanted_name) <= 1:
        raise HTTPException(status_code = 400, detail= "Query parameter not valid")
    
    # ricerca per cognome
    response = requests.get(f"{data_service_url_base}/players?name={wanted_name}")
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code, detail=response.text)
    suggested_players = response.json()
    return suggested_players if suggested_players else []

 
@app.get("/all-players", summary = "Return all Players in the application", response_model = list[Player])
def getAllPlayers():
    response = requests.get(f"{data_service_url_base}/players/")
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code, detail = response.json()['detail'])
    return response.json()


@app.get("/by-league", summary = "Get the squads of the given league and optionally for the user, logged or given", response_model = list[Squad])
def get_squads_by_league(league_id: int, logged_user: dict = Depends(verify_token), user_id: Optional[int] = None, of_user: Optional[bool] = False):
    
    params = {}

    if of_user: 
        logged_user_id = logged_user['user_id']

        # if user_id is passed take it, else take the logged user
        owner_id = user_id if user_id else logged_user_id 

        params = {'league_id': league_id, 'user_id': owner_id}
    else:
        params = {'league_id': league_id} # just league

    # get squads by league
    response = requests.get(f"{data_service_url_base}/squads", params=params)
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code, detail = "Unable to get squads in league")
    squads = response.json()
    return squads

'''
# TODO: TEST - Optional se vogliamo
@app.patch("/{squad_id}/add_player", summary = "Add a player to a squad")
def add_player_to_squad(squad_id: int, player_body: dict, logged_user: dict = Depends(verify_token)):
    user_id = logged_user["user_id"]

    # get squad from squad_id
    response = requests.get(f"{data_service_url_base}/squads/{squad_id}")
    if response.status_code != 200:
        raise HTTPException(status_code = 404, detail = "Squad not found")
    squad = response.json()

    # authorization : user loggato è admin della lega ?
    response = requests.get(f"{data_service_url_base}/leagues/{squad.league_id}")
    if user_id != response.json()['owner_id']:
        raise HTTPException(status_code = 403, detail="Action is Forbidden for the logged user")
    
    # TODO: aggiunti giocatore alla rosa
'''


@app.get("/{squad_id}", summary = "Get a Squad with or without players", response_model = dict)
def get_squad_by_id(squad_id:int, with_players: bool=False):
    if with_players:
        response = requests.get(f"{data_service_url_base}/squads/{squad_id}/with-players")
    else:
        response = requests.get(f"{data_service_url_base}/squads/{squad_id}")
    
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code, detail = response.json()['detail'])
    return response.json()


@app.get("/{squad_id}/last-scores", summary = "Get the last 3 scores of the squad, given the matchday from start", response_model = list[SquadScore])
def get_last_scores(squad_id: int, matchday_number: int):
    
    results = list()
    n_last_scores = 3 # ultimi 3 risultati
    for i in range(1,n_last_scores+1):
        matchday_to_search = matchday_number - i
        # get matchday id:
        response = requests.get(f"{data_service_url_base}/matchdays?matchday_number={matchday_to_search}")
        if response.status_code != 200:
            raise HTTPException(status_code = response.status_code, detail = "Matchday not found")
        matchday_id = response.json()[0]['id']

        # get lineup
        res = requests.get(f"{data_service_url_base}/lineups?squad_id={squad_id}&matchDay_id={matchday_id}")
        if (res.status_code != 200) or (len(res.json()) == 0):
            # no lineup per quel matchday
            results.append({'matchday_number': matchday_to_search, 'score': 'S.V.'})
        else:
            lineup = res.json()[0]
            results.append({'matchday_number': matchday_to_search, 'score': lineup['score']})
        
    return results



