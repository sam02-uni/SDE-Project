from fastapi import FastAPI, HTTPException
import requests
import os
from models import LineUpCreate
from dependency import verify_token

app = FastAPI(title= "lineup business service", root_path="/business/lineup")
grades_scraper_service_url_base = os.getenv("GRADES_SCRAPER_URL_BASE", "http://grades-scraper-service:8000")
data_service_url_base = os.getenv("DATA_SERVICE_URL_BASE", "http://data-service:8000")
football_adapter_service_url_base = os.getenv("FOOTBALL_ADAPTER_SERVICE_URL_BASE", "http://football-adatper-service:8000") 


@app.get("/")
def read_root():
    return {"Lineup Business service is running"}

@app.post("/")
def insert_lineup(base_line_up: LineUpCreate):  # insert lineup for the current user and current matchday
    # TODO: trova id user corrente
    # TODO: trova squad_id di user corrente nella lega se squad_id non presente in base_line_up
    # TODO: controlli numero giocatori e matchday
    pass
    

@app.get("/{lineup_id}/grades")
def get_lineup_grades(lineup_id: int): # get the grades (stored in db) for the given lineup
    update_grades()  # update in back

    # get lineup from data service
    response = requests.get(f"{data_service_url_base}/lineups/{lineup_id}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="LineUp not found")
    lineup_with_players = response.json()  
    players = lineup_with_players['players'] # list of {is_starting: bool, player: Player}

    result = []
    # for each player get his rating for that matchday
    for player_in_lineup in players:
        print(player_in_lineup)
        response = requests.get(f"{data_service_url_base}/players/rating?matchday_id={lineup_with_players['matchday_id']}&player_id={player_in_lineup['player']['id']}")
        if response.status_code != 200: # player rating not in the db
            result.append({'is_starting':player_in_lineup['is_starting'], 'player': player_in_lineup['player'], 
                           'real_rating': None, 'fanta_rating': None})
            continue

        player_rating = response.json()[0] # is a list

        result.append({'is_starting':player_in_lineup['is_starting'], 'player': player_in_lineup['player'], 
                       'real_rating': player_rating['real_rating'], 'fanta_rating': player_rating['fanta_rating']})
        
    return result

             


# TODO: TEST solo la parte in cui fa il taglio dei players to grade
@app.get("/update_grades") 
def update_grades():  # aggiorna i voti dei giocatori per la giornata corrente
 
    # check how many matches of the current matchday have been played so far online
    response = requests.get(f"{football_adapter_service_url_base}/matchday_info")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Unable to get current matchday info")
    actual_matchday_info = response.json()
    print("actual matchday is:", actual_matchday_info['currentMatchday'])

    response = requests.get(f"{data_service_url_base}/matchdays?matchday_number={actual_matchday_info['currentMatchday']}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Matchday not found")
    matchday_db_id = response.json()[0]['id']

    # get how many matches have been registered and graded in local db so far
    response = requests.get(f"{data_service_url_base}/matchdays/{matchday_db_id}/status")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Matchday status not found")
    matchday_db_status = response.json()

    # if the local value is lower than the actual value, get the new matches (teams):
    if matchday_db_status['played_so_far'] >= actual_matchday_info['played']:
        return {"status": "There are no new matches whose grades has to be added"}
    else:
        negative_difference = int(matchday_db_status['played_so_far'] - actual_matchday_info['played'])
        response = requests.get(f"{football_adapter_service_url_base}/finished_matches/{actual_matchday_info['currentMatchday']}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Unable to get finished matches info")
        matches = response.json()
        not_graded_matches = matches[negative_difference:] # new matches whose teams players have to be graded
        print("not graded matches:", not_graded_matches)

        # prendi che squadre sono: solo per giocatori di queste squadre inserisci i voti
        teams = {m['homeTeam'] for m in not_graded_matches} | {m['awayTeam'] for m in not_graded_matches}
        print(teams)
    
        response = requests.get(f"{grades_scraper_service_url_base}/scrape_grades/{actual_matchday_info['currentMatchday']}")
        if response.status_code != 200:
            error = response.json()
            raise HTTPException(status_code=response.status_code, detail=f"Unable to scrape grades: {error.get('detail', 'Server error')}")
        
        players_scraped = response.json()

        #matchday = players_scraped['matchday']
        #response = requests.get(f"{data_service_url_base}/matchdays?matchday_number={matchday}")
        #if response.status_code != 200:
        #    raise HTTPException(status_code=response.status_code, detail="Matchday not found")
        #matchday_db_id = response.json()[0]['id']

        player_scraped_to_grade = [
            p for p in players_scraped if any(p['squad_name'].lower() in team.lower() for team in teams)
        ]


        # associazione dei nomi e caricamento del rating
        for player_scraped in players_scraped:
            response = requests.get(f"{data_service_url_base}/players?name={player_scraped['player_surname']}&serie_a_team={player_scraped['squad_name']}")
            if response.status_code != 200:
                continue # non carico voto
            players_found_db = response.json()
            if len(players_found_db) == 0:
                print("non trovato giocatore:", player_scraped['player_surname'])
                continue # non carico voto

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
        
        # update the matchday status:
        response = requests.patch(f"{data_service_url_base}/matchdays/{matchday_db_id}", json={"played_so_far": actual_matchday_info['played']})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Unable to update matchday status")
        
        return {"status": "Grades updated successfully"}

# calcolo punteggio per formazione
@app.get("/{lineup_id}/calculate_score")
def calculate_score(lineup_id: int):

    response = requests.get(f"{data_service_url_base}/lineups/{lineup_id}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="LineUp not found")
    lineup_with_players = response.json()
    
    # il matchday è concluso?
    response = requests.get(f"{data_service_url_base}/matchdays/{lineup_with_players['matchday_id']}")
    matchday = response.json()
    response = requests.get(f"{football_adapter_service_url_base}/matchday_info?matchday={matchday['number']}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Unable to get matchday info")
    
    matchday_info = response.json()
    if not matchday_info['lastMatchFinished']:
        raise HTTPException(status_code=400, detail="Matchday not finished yet")
    
    # calcolo punteggio totale della formazione , TODO: calcolo anche panchinari
    score = 0
    players_in_lineup = lineup_with_players['players']
    for player in players_in_lineup:
        if player['is_starting']: # titolare
            actual_player = player['player']
            response = requests.get(f"{data_service_url_base}/players/rating?matchday_id={lineup_with_players['matchday_id']}&player_id={actual_player['id']}")
            if response.status_code != 200: # player rating not in the db = non ha giocato
                continue

            # fantavoto lo ha ? 
            rating = response.json()[0]
            if not( rating['fanta_rating'] > 0):
                # non lo ha : ha giocato troppo poco 
                # TODO cambia qui sotto per regola fanta dello scambio con panchinaro
                continue

            score += rating['fanta_rating']

    # update lineup score in db
    response = requests.patch(f"{data_service_url_base}/lineups/{lineup_with_players['id']}", json={"score": score, "players": None})
    if response.status_code != 200:
        print(response.json())
        raise HTTPException(status_code = response.status_code, detail = "Not able to update score of the lineup")
    
    # update squad score in db
    response = requests.patch(f"{data_service_url_base}/squads/{lineup_with_players['squad_id']}?add_score=true", json={"score": score, "name": None})
    if response.status_code != 200:
        print(response.json())
        raise HTTPException(status_code = response.status_code, detail = "Not able to update score of the squad")
    
    return {'score_lineup': score}
 

        

    