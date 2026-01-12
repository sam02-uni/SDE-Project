import requests
import os

class FootballAPIClient:
    def __init__(self):
        self.api_key = os.getenv("FOOTBALL_API_KEY")
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {'x-apisports-key': self.api_key}

    def get_players_by_team(self, team_id: int):
        # Esempio: Serie A (League 135) - Season 2025
        # get("https://v3.football.api-sports.io/players?season=2018&league=61&team=33");
        params = {'team': team_id, 'league': 135, 'season': 2025}
        response = requests.get(f"{self.base_url}/players", headers=self.headers, params=params)
        return response.json().get('response', [])