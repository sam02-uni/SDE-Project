# Business Logic Service for the League Management
from fastapi import FastAPI, HTTPException, Depends, Body
import requests
import os
import json
from models import BaseLeagueModel, emailParticipant, EssentialLeagueInfo, League, TableSquadInfo
from dependency import verify_token
from typing import Optional

tags_metadata = [ # for the Swagger documentation
    ]

app = FastAPI(title="League Business Service", openapi_tags=tags_metadata, root_path="/business/leagues") 

data_service_url_base = os.getenv("DATA_SERVICE_URL_BASE", "http://data-service:8000")
football_adapter_service_url_base = os.getenv("FOOTBALL_ADAPTER_SERVICE_URL_BASE", "http://football-adatper-service:8000") 

@app.get("/")
def read_root():  
    return {"message": "League Business Service is running"}

@app.get("/by-name")
def get_league_by_name(name: str, user: dict = Depends(verify_token)): # name query parameter
    # TODO
    user_id = user["user_id"]
    print(user_id)
    pass

@app.get("/by_user", response_model=list[EssentialLeagueInfo], summary = "Get the league whose owner or participant is the user, logged or given")
def get_leagues_by_user(not_logged_user_id: Optional[int] = None, as_participant : Optional[bool] = False, user: Optional[dict] = Depends(verify_token)): 
    params = {}
    if as_participant:
        params.update({'as_participant': 'true'})
    if not_logged_user_id:
        params.update({'user_id': not_logged_user_id})
    else:
        logged_user_id = user['user_id']
        params.update({'user_id': logged_user_id})       
    response = requests.get(f"{data_service_url_base}leagues", params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Not found")
    return response.json()

@app.get("/current_matchday")
def get_current_matchday_info():
    response = requests.get(f"{football_adapter_service_url_base}/matchday_info")
    if response.status_code != 200:
        return {"error": "unable to fetch current matchday info"}
    
    return response.json()

@app.get("/{league_id}", response_model=League)
def get_league_details(league_id: int):
    league_data = requests.get(f"{data_service_url_base}leagues/{league_id}").json()
    return league_data

@app.post("/", response_model=int, status_code=201) # response model è l'id della lega creata 
def create_league(league_data: BaseLeagueModel, user: dict = Depends(verify_token)): # league_data contiene name, max_credits
    
    user_id = user['user_id']
    print(user_id)
    payload = dict(name=league_data.name, max_credits=league_data.max_credits, owner_id=user_id) 
    response = requests.post(f"{data_service_url_base}leagues", json=payload)
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail="Not created")
    new_league = response.json()

    # add owner as participant
    #response = requests.post(f"{data_service_url_base}leagues/{new_league['id']}/participants", json=new_league['owner_id'])
    #if response.status_code !=201:
    #    raise HTTPException(status_code=response.status_code, detail="Ownwe not added as participant")
    
    print(new_league)
    return new_league["id"]

# TODO: TEST
@app.delete("/{league_id}")
def delete_league(league_id: int, user: dict = Depends(verify_token)):
    logged_user_id = user['user_id']

    # is logged user the admin of the league ? 
    league_info = requests.get(f"{data_service_url_base}leagues/{league_id}").json()
    if league_info['owner_id'] != logged_user_id:
        raise HTTPException(status_code=403, detail="The logged user is not the admin of this league")
    
    # delete league
    res = requests.delete(f"{data_service_url_base}leagues/{league_id}")
    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail="Unable to delete this League")
    
    return res.json()
    

@app.patch("/{league_id}") # update impostazioni lega SI PUO EVITARE DI FARE
def update_league(league_id: int):
    pass

@app.get("/{league_id}/logged-owner", response_model=dict) # is the logged user the owner of the league?
def is_logged_user_league_owner(league_id: int, user: dict = Depends(verify_token)):
    logged_user_id = user['user_id']
    response = requests.get(f"{data_service_url_base}leagues/{league_id}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="League not found")
    if response.json()['owner_id'] == logged_user_id:
        return {'is_owner': True}
    return {'is_owner': False}

@app.get("/{league_id}/table", response_model=list[TableSquadInfo]) # classifica della lega
def get_league_table(league_id: int):
    squads_data = requests.get(f"{data_service_url_base}squads?league_id={league_id}").json()
    print(squads_data)
    sortered_squad_dict = sorted(squads_data, key=lambda x: x['score'], reverse=True) # sort per scores in descending
    return sortered_squad_dict

@app.post("/{league_id}/participants", status_code=201) # aggiunge partecipante alla lega
def add_league_participant(league_id: int, email_participant: emailParticipant, user: dict = Depends(verify_token)): # email in body

    # logged user is an admin of the league?
    user_id = user['user_id']
    league_info = requests.get(f"{data_service_url_base}leagues/{league_id}").json()
    if league_info['owner_id'] != user_id:
        raise HTTPException(status_code=403, detail="The logged user is not the admin of this league")
    
    # get participant id
    response = requests.get(f"{data_service_url_base}users/by-email?user_email={email_participant.email_participant}")
    if response.status_code != 200:
        print(response.json())
        raise HTTPException(status_code=response.status_code, detail="User with this email not found")
    participant = response.json()
    
    # al league data service passare id_lega e id_partecipante
    response = requests.post(f"{data_service_url_base}leagues/{league_id}/participants", json=participant['id'])
    if response.status_code !=201:
        raise HTTPException(status_code=response.status_code, detail="User not added as participant")
    
    return response.json() # return LeagueWithParticipants directly from data service
    
# TODO: TEST
@app.delete("/{league_id}/participants/by-email", summary = "delete a participant using the email")
def delete_participant_by_mail(league_id: int, email: str):
    # authorization ?

    # get id of the participant
    res = requests.get(f"{data_service_url_base}users/by-email?user_email={email}")
    if res.status_code != 200:
        raise HTTPException(status_code = res.status_code, detail= "User not found")
    
    id_participant = res.json()['id']

    # delete from league
    res = requests.delete(f"{data_service_url_base}leagues/{league_id}/participants/{id_participant}")
    if res.status_code != 200:
        raise HTTPException(status_code = res.status_code, detail = res.json().get("detail", "Unable to delete participant"))
    
    return {'detail': 'deleted successfully', 'deleted_participant_id': id_participant}