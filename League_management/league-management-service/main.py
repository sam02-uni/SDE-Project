from fastapi import FastAPI
import requests
import os
import json

# TODO: definire i modelli di request e response in models.py

app = FastAPI(title="League managament process centric service", root_path = "/process/league-management")

league_service_url_base = os.getenv("LEAGUE_SERVICE_URL_BASE", "http://league-service:8004")

@app.get("/")
def read_root():
    return {"League management process service is Running!"}


@app.post("/process/league-management/init", response_model=str) # restituisce id alla gui, la gui salva id in LocalStorage
def init_base_league():
    # crea lega con nome e max_credits inseriti dall admin nella gui
    pass

@app.post("/process/league-management/{league_id}/add_participant")
def add_partiticant_to_league(league_id: int):
    # riceve: league_id, email utente, lista di giocatori, nome della rosa
    # aggiunge un utente con rosa relativa alla lega
    #  TODO
    # ENDPOINT in Business User o Auth per verificare che email esiste 
    # League business per aggiungere partecipante alla lega
    # Squad business per creare rosa di utente in lega
    # return ok
    pass

# usato quando utente scrive nome nella casella di testo e 'cerca' e restituisce i giocatori con quei nomi
@app.get("/process/league-management/suggest_players")
def suggest_players(given_name:str):
    pass
