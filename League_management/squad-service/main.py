from fastapi import FastAPI, HTTPException
import requests
import os
from models import SquadCreate 


app = FastAPI(title="Squad Business service", root_path = "/business/squads")
data_service_url_base = os.getenv("DATA_SERVICE_URL_BASE", "http://data-service:8000")

@app.get("/")
def read_root():
    return {"squad business service is running"}

# creazione di una rosa associata ad una lega e ad un utente
@app.post("/", status_code=201)
def create_squad(info: SquadCreate):
    # minimum number of players check
    '''players = info.players
    g, d, m, a = 0
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

    if g < 3 or d < 6 or m < 6 or a < 6:
        raise HTTPException(status_code = 400, detail="Not enough players in squad")
    '''

    # call data service to create squad
    response = requests.post(f"{data_service_url_base}/squads/with_players", json=info.model_dump())
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

# aggiunta di un giocatore ad una rosa
@app.patch("/{squad_id}/add_player")
def add_player_to_squad():
    pass

