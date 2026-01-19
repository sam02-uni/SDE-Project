from fastapi import FastAPI
import requests
import os
import json

# TODO: definire i modelli di request e response

app = FastAPI(title="Squad Business service", root_path = "/business/squads")

@app.get("/")
def read_root():
    return {"squad business service is running"}

# creazione di una rosa associata ad una lega e ad un utente
@app.post("/business/squads")
def create_squad():
    pass    

# aggiunta di un giocatore ad una rosa
@app.patch("/business/squads/{squad_id}/add_player")
def add_player_to_squad():
    pass

