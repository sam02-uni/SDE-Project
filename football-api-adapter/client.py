import requests
import os
import json

class FootballAPIClient:
    def __init__(self):
        self.api_key = os.getenv("FOOTBALL_API_KEY")
        self.base_url = "http://api.football-data.org/v4" # Football api : https://v3.football.api-sports.io
        self.headers = {'X-Auth-Token': self.api_key}

    def get_players_by_team(self, team_id: int):
        # 2019 : id della Serie A
        url = f"{self.base_url}/teams/{team_id}"
        response = requests.get(url, headers=self.headers)

        # Debug rapido
        if response.status_code != 200:
            print(f"Errore API: {response.status_code} - {response.text}")
            return []
        
        response_dict = response.json()
        
        return{
            "name": response_dict["name"],
            "squad": response_dict["squad"]
        }
    
    # TODO: TEST
    def get_current_matchday(self, competition_id):
        url = f"{self.base_url}/competitions/{competition_id}"
        response = requests.get(url, headers=self.headers)

        # Debug rapido
        if response.status_code != 200:
            print(f"Errore API: {response.status_code} - {response.text}")
            return []
        
        return response.json()['currentSeason']['currentMatchday']

    # TODO: TEST
    def get_matchday_info(self, competiton_id):

        # get current matchday
        matchday = self.get_current_matchday(competition_id=competiton_id)

        # get infos
        url = f"{self.base_url}/competitions/{competiton_id}/matches?matchday={matchday}"
        response = requests.get(url, headers=self.headers)

        # Debug rapido
        if response.status_code != 200:
            print(f"Errore API: {response.status_code} - {response.text}")
            return []
        
        response_dict = response.json()

        first_match_started = False if response_dict['matches'][0]['status'] in ('SCHEDULED', 'TIMED') else True 
        
        return {
            'currentMatchday': matchday,
            'count' : response_dict['resultSet']['count'],
            'first': response_dict['resultSet']['first'],
            'last': response_dict['resultSet']['last'],
            'played': response_dict['resultSet']['played'],
            'firstMatchStarted': first_match_started
        }
        

    
'''
98 milan
99 fiorentina
100 Roma
102 Atalanta
103 Bologna NO key error: 98606 Sohm sia fiorentina che bologna
104 Cagliari
107 Genoa
108 Inter Carlos Augusto messo male il cognome
109 juventus 
110 Lazio
112
113
115
450
457
471
487
586
5890
7397'''