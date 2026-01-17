# Business Logic Service for the League Management
from fastapi import FastAPI
import requests
import os
import json

tags_metadata = [ # for the Swagger documentation
    ]

# TODO: define the response models and request models
# TODO: implementare controlli di autenticazione e autorizzazione
# TODO: aggiungi in data service - league endpoint per fare get di leghe per utente

app = FastAPI(title="League Business Service", openapi_tags=tags_metadata, root_path="/business/league") 

data_service_url_base = os.getenv("DATA_SERVICE_URL_BASE", "http://fanta-data-service:8001")

@app.get("/business/leagues")
def read_root():  
    return {"message": "League Business Service is running"}

@app.get("/business/leagues/search")
def get_league_by_name(name: str): # name query parameter
    # TODO: chiama il data service per cercare la lega per nome e per utente <- CHIEDI MARIANO in che modo prendo l'utente qui ??
    pass

@app.get("/business/leagues/{league_id}")
def get_league_details(league_id: int):
    league_data = requests.get(f"{data_service_url_base}/leagues/{league_id}").json()
    return league_data

@app.post("/business/leagues", response_model=str) # response model è l'id della lega creata 
def create_league(league_data: dict): # league_data contiene name, max_credits
    # TODO 
    # controllare autenticazione utente
    # prendere id dell'utente loggato : owner_id
    payload = dict(name=league_data["name"], max_credits=league_data["max_credits"], owner_id=1) # TODO owner id
    new_league = requests.post(f"{data_service_url_base}/leagues", json=payload).json()
    return new_league["id"]

@app.delete("/business/leagues/{league_id}")
def delete_league(league_id: int):
    # TODO
    pass

@app.patch("/business/leagues/{league_id}") # update impostazioni lega
def update_league(league_id: int):
    pass

@app.get("/business/leagues/{league_id}/table") # classifica della lega
def get_league_table(league_id: int):
    squads_data = requests.get(f"{data_service_url_base}/squad?league_id={league_id}").json()
    squads_dict = json.loads(squads_data)
    sortered_squad_dict = sorted(squads_dict, key=lambda x: x['score'], reverse=True) # sort per scores in descending
    return json.dumps(sortered_squad_dict)

@app.post("/business/leagues/{league_id}/participants") # aggiunge partecipanti alla lega
def get_league_participants(league_id: int):
    pass