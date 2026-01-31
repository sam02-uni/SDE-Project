# Adapter Service
# Questo servizio è un adapter per interfacciarsi con un'ipotetica Football API esterna
# Fornisce un'API REST per ottenere dati sui giocatori, squadre, partite


import json
from fastapi import FastAPI, HTTPException
import os
from client import FootballAPIClient
import requests
from typing import Optional

class Player():
    id: int 
    name: str
    surname: str 
    role: str
    serie_a_team: str 
    mean_rating: float 

app = FastAPI(title="Football API Adapter", root_path="/adapter/football") 
data_service_url_base = os.getenv("DATA_SERVICE_URL_BASE", "http://fanta-data-service:8001")
client = FootballAPIClient()
mapping_position = {
    "goalkeeper": "G", 
    "defence": "D",
    "left-back": "D",
    "right-back": "D",
    "centre-back": "D",
    "midfield": "M",
    "left midfield": "M",
    "right midfield": "M",
    "defensive midfield": "M",
    "central midfield": "M",
    "attacking midfield": "M",
    "offence": "A",
    "centre-forward": "A",
    "left winger": "A",
    "right winger": "A"
}

@app.get("/")
def read_root():
    return {"Adapter service for football data is running"}

@app.get("/update_players", response_model=dict, status_code=200) # Endpoint to update players in the db data from an external football API
def update_players(team_id: str): # team_id query param
    squad = client.get_players_by_team(team_id=team_id)
    if len(squad) <= 0:
        raise HTTPException(status_code=400, detail="external API Error")
    squad_name = squad["name"]
    players = []
    #print(squad['squad'])
    for player in squad['squad']:
        player_to_db = dict()
        player_to_db["id"] = player["id"]
        player_to_db["mean_rating"] = 0.0

        name_surname = str(player["name"]).split(" ")
        if len(name_surname) < 2:
            player_to_db["name"] = ''
            player_to_db["surname"] = name_surname[0] # se un solo nome lo metto come cognome
        else:
            player_to_db['name'] = name_surname[0] # a name primo nome
            player_to_db["surname"] = ' '.join(nome for nome in name_surname[1:]) # a surname il resto

        position = player["position"]
        if position is None:
            position = "midfield" # default position
        player_to_db["role"] = mapping_position.get(position.lower())

        player_to_db["serie_a_team"] = squad_name
        players.append(player_to_db)
    
    response  = requests.post(f"{data_service_url_base}/players/chunk", json=players)    
    if response.status_code != 201:
        raise HTTPException(status_code=500, detail=f"data service error:{response.text}")
    return {'ok':True}

@app.get("/matchday_info")
def get_matchday_info(matchday: Optional[int] = None):
    info = client.get_matchday_info(competiton_id='2019', matchday_number=matchday)
    return info

@app.get("/finished_matches/{matchday}")
def get_finished_matches(matchday: int):
    matches = client.get_finished_matches(matchday)
    return matches