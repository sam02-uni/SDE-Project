from fastapi import FastAPI, HTTPException, Depends
import requests
import os
from models import LineUpCreate
from dependency import verify_token
from typing import Optional

app = FastAPI(title= "lineup business service", root_path="/business/lineups")
grades_scraper_service_url_base = os.getenv("GRADES_SCRAPER_URL_BASE", "http://grades-scraper-service:8000")
data_service_url_base = os.getenv("DATA_SERVICE_URL_BASE", "http://data-service:8000")
football_adapter_service_url_base = os.getenv("FOOTBALL_ADAPTER_SERVICE_URL_BASE", "http://football-adatper-service:8000") 


@app.get("/")
def read_root():
    return {"Lineup Business service is running"}


@app.get("/by-squad")
def get_lineups_of_squad(squad_id: int, matchday_number: Optional[int] = None):
    # TODO: fare authorization ? discuti con Mariano e Samuele

    matchday_id = None
    if matchday_number:
        # get matchday_id:
        response = requests.get(f"{data_service_url_base}/matchdays?matchday_number={matchday_number}")
        if response.status_code != 200:
                raise HTTPException(status_code = response.status_code, detail = "Matchday not found")
        matchday_id = response.json()[0]['id']

    # get lineups
    response = requests.get(f"{data_service_url_base}/lineups?squad_id={squad_id}&matchday_id={matchday_id}")
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code, detail = "Lineups not found")
    lineups = response.json() # squad with players

    return lineups
    
@app.post("/", status_code = 201)
def insert_lineup(base_line_up: LineUpCreate, user: dict = Depends(verify_token)):  # insert lineup for the current user and matchday specified in lineup object
    # Recupero id dell'utente di sessione
    logged_user_id = user['user_id']

    # Chiamata al db se ho squad_id
    if base_line_up.squad_id != None:
        response = requests.get(f"{data_service_url_base}squads/{base_line_up.squad_id}/with-players")
        if response.status_code != 200:
            raise HTTPException(status_code = response.status_code, detail = "Squad not found")
        squad = response.json() # squad with players
    else:
        # Chiamata al db se ho league_id e non ho squad_id
        if base_line_up.league_id != None: 
            response = requests.get(f"{data_service_url_base}/squads?league_id={base_line_up.league_id}&user_id={logged_user_id}")
            if response.status_code != 200:
                raise HTTPException(status_code = response.status_code, detail = "Squad not found")
            squad_id = response.json()[0]['id'] 
            response = requests.get(f"{data_service_url_base}/squads/{squad_id}/with-players")
            squad = response.json() # squad with players
        else:
            # Sollevo eccezione per Bad request
            raise HTTPException(status_code = 400, detail = "Bad request")

    
    # Verifica che l'utente di sessione sia il proprietario della squadra
    if logged_user_id == squad['owner_id']:
        
        response = requests.get(f"{data_service_url_base}/matchdays?matchday_number={base_line_up.matchday_number}")
        if response.status_code != 200:
            raise HTTPException(status_code = response.status_code, detail = response.json().get('detail', 'Not able to get matchday info'))
        matchday_id_for_lineup = response.json()[0]['id']

        # Verifica che il matchday esiste
        if response.status_code == 200:

            # verifica se formazione per la giornata à gia inserita
            response = requests.get(f"{data_service_url_base}/lineups?squad_id={squad['id']}&matchDay_id={matchday_id_for_lineup}")
            if (response == 200) and ( len(response.json()) >= 1) : # già presente
                raise HTTPException(status_code = 400, detail = "Lineup already inserted for this matchday")
            


            # Verifica sul numero di giocatori inseriti per la formazione
            if len(base_line_up.starting_ids) == 11 :#and len(base_line_up.bench_ids) == 7:
                lineup = set(base_line_up.starting_ids + base_line_up.bench_ids) # set of player ids in lineup
                squad_ids = [player['id'] for player in squad['players']]
                squad_set = set(squad_ids)
                # Verifica che tutti i giocatori appartengono alla squadra
                if (lineup.issubset(squad_set)):
                    # Creazione del dict da mandare al db
                    lineUpPlayer = {
                        'squad_id': squad['id'],
                        'matchday_id': matchday_id_for_lineup,
                        'players': [] 
                    }

                    for playerId in base_line_up.starting_ids:
                        response = requests.get(f"{data_service_url_base}/players/{playerId}")
                        player = response.json()
                        lineUpPlayer["players"].append({
                            'is_starting': True, 
                            'player': player
                        })
                    
                    for playerId in base_line_up.bench_ids:
                        response = requests.get(f"{data_service_url_base}/players/{playerId}")
                        player = response.json()
                        lineUpPlayer["players"].append({
                            'is_starting': False, 
                            'player': player
                        })
                    # Richiesta di inserimento al db
                    postResponse = requests.post(f"{data_service_url_base}/lineups", json=lineUpPlayer)
                    if postResponse.status_code != 201:
                        raise HTTPException(status_code = postResponse.status_code, detail = postResponse.json()['detail'])
                    return postResponse.json()
                
                else:
                    raise HTTPException(status_code = 400, detail = "Bad request")
            else:
                raise HTTPException(status_code = 400, detail = "Bad request")    
        else:
            raise HTTPException(status_code = 400, detail = "Bad request")
    else:
        raise HTTPException(status_code = 403, detail = "User is not the owner")
    

@app.get("/{lineup_id}/grades")
def get_lineup_grades(lineup_id: int): # get the grades (stored in db) for the given lineup

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

             
@app.get("/update_grades") 
def update_grades(matchday_id: int):  # aggiorna i voti di tutti giocatori per la giornata fornita
 
    # matchday in db
    response = requests.get(f"{data_service_url_base}/matchdays/{matchday_id}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Matchday not found")
    matchday_db = response.json()

    # check how many matches of the matchday have been played so far online
    response = requests.get(f"{football_adapter_service_url_base}/matchday_info?matchday={matchday_db['number']}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Unable to get matchday info")
    actual_matchday_info = response.json()
    print("actual matchday is:", actual_matchday_info['currentMatchday'])

    # get how many matches have been registered and graded in local db so far
    response = requests.get(f"{data_service_url_base}/matchdays/{matchday_db['id']}/status")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Matchday status not found")
    matchday_db_status = response.json()

    # if the local value is lower than the actual value, get the new matches (teams):
    if matchday_db_status['played_so_far'] >= actual_matchday_info['played']:
        return {"status": "There are no new matches whose grades has to be added"}
    else:
        print("there are new matches to be graded")
        negative_difference = int(matchday_db_status['played_so_far'] - actual_matchday_info['played'])
        response = requests.get(f"{football_adapter_service_url_base}/finished_matches/{actual_matchday_info['currentMatchday']}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Unable to get finished matches info")
        matches = response.json()
        not_graded_matches = matches[negative_difference:] # new matches whose teams players have to be graded
        #print("not graded matches:", not_graded_matches)

        # prendi che squadre sono: solo per giocatori di queste squadre inserisci i voti
        teams = {m['homeTeam'] for m in not_graded_matches} | {m['awayTeam'] for m in not_graded_matches}
        print("Not graded teams: ",teams)
    
        response = requests.get(f"{grades_scraper_service_url_base}/scrape_grades/{actual_matchday_info['currentMatchday']}")
        if response.status_code != 200:
            error = response.json()
            raise HTTPException(status_code=response.status_code, detail=f"Unable to scrape grades: {error.get('detail', 'Server error')}")
        
        players_scraped = response.json()['grades']

        #matchday = players_scraped['matchday']
        #response = requests.get(f"{data_service_url_base}/matchdays?matchday_number={matchday}")
        #if response.status_code != 200:
        #    raise HTTPException(status_code=response.status_code, detail="Matchday not found")
        #matchday_db_id = response.json()[0]['id']

        players_scraped_to_grade = [
            p for p in players_scraped if any(p['squad_name'].lower() in team.lower() for team in teams)
        ]


        # associazione dei nomi e caricamento del rating
        for player_scraped in players_scraped_to_grade:
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
                    matchday_id=matchday_db['id'],
                    real_rating=player_scraped['grade'],
                    fanta_rating=player_scraped['fanta_grade']
                )
                response = requests.post(f"{data_service_url_base}/players/rating", json=payload)
                if response.status_code != 201:
                    error_detail = response.json()['detail']
                    print(f"Grade not inserted for player {player_found_db['id']} because of: {error_detail}")
                    #raise HTTPException(status_code=response.status_code, detail=f"Grade not inserted because of: {error_detail}")
        
        # update the matchday status:
        response = requests.patch(f"{data_service_url_base}/matchdays/status/{matchday_db['id']}", json={"played_so_far": actual_matchday_info['played']})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Unable to update matchday status")
        
        return {"status": "Grades updated successfully"}

# calcolo punteggio per formazione
# TEST : parte di calcolo panchinari
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
    
    # se già stato calcolato per questa giornata:
    if lineup_with_players['score'] != 0:
        return lineup_with_players['score'] 
    
    # calcolo punteggio totale della formazione 
    times_switched = 0 # subentrati, max 3 cambi
    score = 0
    players_in_lineup = lineup_with_players['players']
    starting_players = [player for player in players_in_lineup if player['is_starting']]
    bench_players = [player for player in players_in_lineup if not player['is_starting']]
    counted_bench_players = set() # qui ids di player dalla panchina che consideriamo per il calcolo finale
    for player in starting_players:
        actual_player = player['player']
        # recupero voto titolare
        res = requests.get(f"{data_service_url_base}/players/rating?matchday_id={lineup_with_players['matchday_id']}&player_id={actual_player['id']}")
        rating_data = res.json()[0] if res.status_code == 200 else None
        
        # Se non ha voto (None) o voto non valido (<= 0)
        if not rating_data or rating_data['fanta_rating'] <= 0: # TODO: se cambi in -1 per i SV qui metti < non <=
            # se può ancora fare cambi:
            if times_switched >= 3:
                score += 0
            found_sub = False
            for bench_p in bench_players:
                b_id = bench_p['player']['id']
                # Controllo ruolo e che non sia già entrato
                if bench_p['player']['role'] == actual_player['role'] and b_id not in counted_bench_players:
                    res_b = requests.get(f"{data_service_url_base}/players/rating?matchday_id={lineup_with_players['matchday_id']}&player_id={b_id}")
                    b_rating_data = res_b.json()[0] if res_b.status_code == 200 else None
                    
                    if b_rating_data and b_rating_data['fanta_rating'] > 0:
                        score += b_rating_data['fanta_rating']
                        counted_bench_players.add(b_id) # SEGNA COME USATO
                        found_sub = True
                        times_switched += 1
                        break
            if not found_sub:
                score += 0 # Nessun sostituto valido
        else:
            score += rating_data['fanta_rating']


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

# TODO: TEST
@app.get("/{lineup_id}")
def get_lineup(lineup_id: int):

    res = requests.get(f"{data_service_url_base}/lineups/{lineup_id}")
    if res.status_code != 200:
        raise HTTPException(status_code = res.status_code, detail = "Lineup not found")
    
    return res.json()

 

        

    