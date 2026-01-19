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
    
'''
98 milan
99 fiorentina
100
102
103
104
107
108
109
110
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