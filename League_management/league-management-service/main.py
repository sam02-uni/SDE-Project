from fastapi import FastAPI, HTTPException
import requests
import os
import json
from models import BaseLeagueModel, ParticipantUserWithSquad

# TODO: definire i modelli di request e response in models.py

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

@app.post("/{league_id}/add_participant", status_code=201, response_model=str)
def add_partiticant_to_league(league_id: int, participantWithSquad: ParticipantUserWithSquad):
    # league_id in PATH , email utente, lista di giocatori, nome della rosa in BODY
    # aggiunge un utente con rosa relativa alla lega
    
    # ENDPOINT in Business User per verificare che email esiste in db
    #  TODO

    # League business per aggiungere partecipante alla lega
    # TODO

    # Squad business per creare rosa di utente in lega
    # TODO

    # return ok
    pass

# usato quando utente scrive nome nella casella di testo e 'cerca' e restituisce i giocatori con quei nomi
@app.get("/suggest_players")
def suggest_players(given_name:str):
    response = requests.get(f"{squad_service_url_base}/business/squads/suggest_player?wanted_name={given_name}")
    return response.json()