from fastapi import FastAPI, HTTPException
import requests
import os
from models import LineUpCreate

app = FastAPI(title= "lineup business service", root_path="/business/lineup")
grades_scraper_service_url_base = os.getenv("GRADES_SCRAPER_URL_BASE", "http://grades-scraper-service:8000")
data_service_url_base = os.getenv("DATA_SERVICE_URL_BASE", "http://data-service:8000")
football_adapter_service_url_base = os.getenv("FOOTBALL_ADAPTER_SERVICE_URL_BASE", "http://football-adatper-service:8000") # TODO add in Compose


@app.get("/")
def read_root():
    return {"Lineup Business service is running"}

@app.post("/")
def insert_lineup(base_line_up: LineUpCreate):  # insert lineup for the current user and current matchday
    # TODO: trova id user corrente
    # TODO: trova squad_id di user corrente nella lega se squad_id non presente in base_line_up
    # TODO: controlli numero giocatori e matchday
    pass
    

# nell'endpoint get_voti (quelli non a fine giornata ma a fine partita se li vuole vedere l'utente)prima controlli sul db e poi se non ci sono li prendi da scraper e salvi e returni
#@app.get("/get_grades")
# controlla nell'attuale matchday quante partite sono concluse, controlla nel metchday API se sono conluse altre partite
# se si chiama /update_grades che richiama lo scraper e aggiorna i voti nel data service (PlayerRating)
# se no ritorna i voti presenti nei PlayerRating (se presente per quel giocatore) per ogni player nella lineup 


@app.get("/update_grades") 
def update_grades():  # aggiorna i voti dei giocatori per la giornata corrente
    # TODO: trovare un modo per prendere i voti solo se effettivamente potrebbe cambiare qualcosa
    # cioè controllare sul db quante partite di matchday corrente sono state giocate (controllare MatchDayStatus.played_so_far), chiamare api football e controllare valore reale
    # se più grande:
    # chiama football adapter api per get_matches_played e prendi [numero partite played da api - MatchDayStatus.played_so_far] partite dalla fine della lista
    # controlle che squadre sono: solo per giocatori di queste squadre inserisci i voti
    response = requests.get(f"{grades_scraper_service_url_base}/scrape_grades/22")
    players_scraped = response.json()

    matchday = players_scraped['matchday']
    response = requests.get(f"{data_service_url_base}/matchdays?matchday_number={matchday}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Matchday not found")
    matchday_db_id = response.json()[0]['id']

    players_scraped = players_scraped['grades']   # squad_name, player_surname, grade, fanta_grade

    # associazione dei nomi
    for player_scraped in players_scraped:
        response = requests.get(f"{data_service_url_base}/players?name={player_scraped['player_surname']}&serie_a_team={player_scraped['squad_name']}")
        if response.status_code != 200:
            continue # non carico voto
        players_found_db = response.json()
        if len(players_found_db) == 0:
            print("non trovato giocatore:", player_scraped['player_surname'])
            continue # non carico voto
        #print("arrivato qui:", player_scraped['player_surname'])

        # 1 o più giocatori comunque li metto lo stesso voto a tutti
        for player_found_db in players_found_db:
            payload = dict(
                player_id=player_found_db['id'],
                matchday_id=matchday_db_id,
                real_rating=player_scraped['grade'],
                fanta_rating=player_scraped['fanta_grade']
            )
            response = requests.post(f"{data_service_url_base}/players/rating", json=payload)
            if response.status_code != 201:
                error_detail = response.json()['detail']
                print(f"Grade not inserted for player {player_found_db['id']} because of: {error_detail}")
                #raise HTTPException(status_code=response.status_code, detail=f"Grade not inserted because of: {error_detail}")
          
    return {"message": "Grades updated successfully"}
            

# calcolo punteggio per formazione
@app.get("/{lineup_id}/calculate_score")
def calculate_score(lineup_id: int):

    response = requests.get(f"{data_service_url_base}/lineups/{lineup_id}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="LineUp not found")
    lineup = response.json()
    
    # il matchday è concluso?
    response = requests.get(f"{data_service_url_base}/matchdays/{lineup['matchday_id']}")
    matchday = response.json()

    response = requests.get(f"{football_adapter_service_url_base}/current_matchday_info")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Unable to get current matchday info")
    
    matchday_info = response.json()
    if not matchday_info['lastMatchFinished']:
        raise HTTPException(status_code=400, detail="Matchday not finished yet")
    
    # calcolo punteggio totale della formazione
    # TODO: recupera dal data service tutti i PlayerRating per ogni Player nella lineup (titolari e panchina) e fai la somma
    # la somma applicala allo score della LINEUP (TODO: Aggiorna DB) e della SQUAD

    