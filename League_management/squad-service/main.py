from fastapi import FastAPI, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
import requests
import os
from models import SquadCreate 
from dependency import verify_token


app = FastAPI(title="Squad Business service", root_path = "/business/squads")
data_service_url_base = os.getenv("DATA_SERVICE_URL_BASE", "http://data-service:8000")

@app.get("/")
def read_root():
    return {"squad business service is running"}

# creazione di una rosa associata ad una lega e ad un utente
@app.post("/", status_code=201) # POST /business/squads
def create_squad(info: SquadCreate, logged_user : dict = Depends(verify_token)):
    print("AISFSJDGJSDGJSJDGJDSFGJ")
    user_id = logged_user['user_id']
    # minimum number of players check
    '''players = info.players
    g, d, m, a = 0,0,0,0
    for player in players:
        match player.role:
            case "G":
                g=+1
                continue
            case "D":
                d=+1
                continue
            case "M":
                m=+1
                continue
            case "A":
                a=+1
                continue

    if g < 3 or d < 6 or m < 6 or a < 6: # 21 giocatori
        raise HTTPException(status_code = 400, detail="Not enough players in squad")
    '''
    # authorization : user loggato è admin della lega ?
    response = requests.get(f"{data_service_url_base}/leagues/{info.league_id}")
    if response.status_code != 200:
        raise HTTPException(status_code = 400, detail="Bad Request: the squad league does not exists")
    if user_id != response.json()['owner_id']:
        raise HTTPException(status_code = 403, detail="Action is Forbidden for the logged user")
    print("authorization passed")

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
    

@app.get("/suggest_player") # suggest the players with that name within
def get_suggested_players(wanted_name: str): # wanted_name: query param
    if wanted_name is None or len(wanted_name) <= 1:
        raise HTTPException(status_code = 400, detail= "Query parameter not valid")
    
    # ricerca per cognome
    response = requests.get(f"{data_service_url_base}/players?name={wanted_name}")
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code, detail=response.text)
    suggested_players = response.json()
    return suggested_players if suggested_players else []

@app.get("/allPlayers")
def getAllPlayers():
    response = requests.get(f"{data_service_url_base}/players/")
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code, detail = response.json()['detail'])
    return response.json()

@app.get("/by-league")
def get_squads_by_league(league_id: int):
    response = requests.get(f"{data_service_url_base}/squads?league_id={league_id}")
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code, detail = "Unable to get squads of the league")
    squads = response.json()
    return squads

@app.get("/take_squad/{league_id}")
def get_squad_by_league(league_id:int,  logged_user: dict = Depends(verify_token)):
    user_id = logged_user["user_id"]
    parametri = {
        "league_id" : league_id,
        "user_id" : user_id
    }
    response = requests.get(f"{data_service_url_base}/squads", params=parametri)
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code, detail = response.json()['detail'])
    data = response.json()
    squad_id = data[0]["id"]
    response = requests.get(f"{data_service_url_base}/squads/{squad_id}/with-players", params=parametri)
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code, detail = response.json()['detail'])
    return response.json()

# aggiunta di un giocatore ad una rosa
# TODO: test
# Optional se vogliamo
@app.patch("/{squad_id}/add_player")
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

@app.get("/{squad_id}")
def get_squad_by_id(squad_id:int, with_players: bool=False):
    if with_players:
        response = requests.get(f"{data_service_url_base}/squads/{squad_id}/with-players")
    else:
        response = requests.get(f"{data_service_url_base}/squads/{squad_id}")
    
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code, detail = response.json()['detail'])
    return response.json()


