import requests
import os

class FootballAPIClient:
    def __init__(self):
        self.api_key = os.getenv("FOOTBALL_API_KEY")
        self.base_url = "http://api.football-data.org/v4" # Football api : https://v3.football.api-sports.io
        self.headers = {'X-Auth-Token': self.api_key}
        self.competition_id = '2019' # serie A

    def get_players_by_team(self, team_id: int):
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
    

    def get_current_matchday(self, competition_id):
        url = f"{self.base_url}/competitions/{competition_id}"
        response = requests.get(url, headers=self.headers)

        # Debug rapido
        if response.status_code != 200:
            print(f"Errore API: {response.status_code} - {response.text}")
            return []
        
        return response.json()['currentSeason']['currentMatchday']

    
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
        last_match_finished = True if response_dict['matches'][-1]['status'] == 'FINISHED' else False
        
        return {
            'currentMatchday': matchday,
            'count' : response_dict['resultSet']['count'],
            'first': response_dict['resultSet']['first'],
            'last': response_dict['resultSet']['last'],
            'played': response_dict['resultSet']['played'],
            'firstMatchStarted': first_match_started,
            'lastMatchFinished': last_match_finished
        }
        
    def get_finished_matches(self):

        # get current matchday
        matchday = self.get_current_matchday(competition_id=self.competition_id)

        # get infos
        url = f"{self.base_url}/competitions/{self.competition_id}/matches?matchday={matchday}&status=FINISHED"
        response = requests.get(url, headers=self.headers)

        # Debug rapido
        if response.status_code != 200:
            print(f"Errore API: {response.status_code} - {response.text}")
            return []
        
        matches = response.json()['matches']
        essential_infos = list()

        for match in matches:
            essential_infos.append({'utcDate': match['utcDate'],
                                    'homeTeam': match['homeTeam']['shortName'],
                                    'awayTeam': match['awayTeam']['shortName'],
                                    'score_homeTeam': match['score']['fullTime']['home'],
                                    'score_awayTeam': match['score']['fullTime']['away']
                                    })

        return essential_infos


    
'''
98 milan
99 fiorentina
100 Roma
102 Atalanta
103 Bologna 
104 Cagliari
107 Genoa
108 Inter 
109 juventus 
110 Lazio
112 Parma
113 Napoli
115 udinese
450 hellas verona
457 Cremonese
471 sassuolo
487 Pisa
586 Torino
5890 lecce
7397 como
'''