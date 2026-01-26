# Business Logic Service for the League Management
from fastapi import FastAPI, HTTPException
import requests
import os
import json
from models import BaseLeagueModel

tags_metadata = [ # for the Swagger documentation
    ]


# TODO: implementare controlli di autenticazione e autorizzazione
# TODO: aggiungi in data service - league endpoint per fare get di leghe per utente

app = FastAPI(title="League Business Service", openapi_tags=tags_metadata, root_path="/business/league") 

data_service_url_base = os.getenv("DATA_SERVICE_URL_BASE", "http://data-service:8000")
football_adapter_service_url_base = os.getenv("FOOTBALL_ADAPTER_SERVICE_URL_BASE", "http://football-adatper-service:8000") # TODO add in Compose

@app.get("/")
def read_root():  
    return {"message": "League Business Service is running"}

@app.get("/search")
def get_league_by_name(name: str): # name query parameter
    # TODO: chiama il data service per cercare la lega per nome e per utente <- CHIEDI MARIANO in che modo prendo l'utente qui ??
    pass

@app.get("/by_user")
def get_leagues_by_user():
    # TODO depends on user_id
    pass

@app.get("/{league_id}")
def get_league_details(league_id: int):
    league_data = requests.get(f"{data_service_url_base}/leagues/{league_id}").json()
    return league_data

@app.post("/", response_model=str) # response model è l'id della lega creata 
def create_league(league_data: BaseLeagueModel): # league_data contiene name, max_credits
    # TODO controllare autenticazione utente, prendere id dell'utente loggato : owner_id
    payload = dict(name=league_data["name"], max_credits=league_data["max_credits"], owner_id=1) # TODO owner id
    response = requests.post(f"{data_service_url_base}/leagues", json=payload)
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail="Not created")
    new_league = response.json()
    return new_league["id"]

@app.delete("/{league_id}")
def delete_league(league_id: int):
    pass

@app.patch("/{league_id}") # update impostazioni lega
def update_league(league_id: int):
    pass

# TODO: TEST
@app.get("/{league_id}/table") # classifica della lega
def get_league_table(league_id: int):
    squads_data = requests.get(f"{data_service_url_base}/squad?league_id={league_id}").json()
    squads_dict = json.loads(squads_data)
    sortered_squad_dict = sorted(squads_dict, key=lambda x: x['score'], reverse=True) # sort per scores in descending
    return json.dumps(sortered_squad_dict)

@app.post("/{league_id}/participants", status_code=201) # aggiunge partecipante alla lega
def add_league_participant(league_id: int, email_participant: str): # email in body
    # get participant id
    response = requests.get(f"{data_service_url_base}/users/by_email/{email_participant}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="User with this email not found")
    participant = response.json()
    
    # al league data service passare id_lega e id_partecipante
    response = requests.post(f"{data_service_url_base}/leagues/{league_id}/participants", json=participant['id'])
    if response.status_code !=201:
        raise HTTPException(status_code=response.status_code, detail="User not added as participant")
    
    return response.json() # return LeagueWithParticipants directly from data service
    
# TODO: TEST
@app.get("/current_matchday")
def get_current_matchday_info():
    response = requests.get(f"{football_adapter_service_url_base}/current_matchday_info")
    if response.status_code != 200:
        return {"error": "unable to fetch current matchday info"}
    
    return response.json()