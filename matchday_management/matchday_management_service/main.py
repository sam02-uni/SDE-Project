from fastapi import FastAPI, HTTPException
import requests
import os


app = FastAPI(title = "Matchday Management Service", root_path="/process/matchday_management")
lineup_service_url_base = os.getenv("LINEUP_SERVICE_URL_BASE", "http://lineup-service:8000") # TODO add in Compose
#league_service_url_base = os.getenv("LEAGUE_SERVICE_URL_BASE", "http://league-service:8000") # TODO add in Compose

@app.get("/")
def read_root():  
    return {"message": "MatchDay Management Process Centric service is running"}




