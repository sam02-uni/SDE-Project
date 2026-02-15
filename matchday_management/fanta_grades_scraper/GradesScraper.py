import requests
from bs4 import BeautifulSoup
import random
import time


class GradesScraper():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/121.0"
    ]
    url_current_matchday = "https://www.fantacalcio.it/voti-fantacalcio-serie-a"
    url_matchday = "https://www.fantacalcio.it/voti-fantacalcio-serie-a/2025-26/{}"
    session = requests.Session()

    def scrape_grades(self, matchday_number: int) -> list:

        grades_list = []
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.google.com/" # Fa credere al server che arrivi da Google
        }

        response = self.session.get(self.url_matchday.format(matchday_number), headers=headers, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:

            soup = BeautifulSoup(response.text, 'html.parser')
            
            tabelle = soup.find_all('table', class_='grades-table')

            # check if at least one table is present:
            if len(tabelle) <= 0:
                print("Nessuna tabella dei voti trovata nella pagina.")
                return grades_list

            for tabella in tabelle:
                # squad name:
                squad_name = tabella.find('thead').select_one('a.team-name.team-link').get_text(strip=True)

                body_tabella = tabella.find('tbody')
                for riga in body_tabella.find_all('tr')[:-1]: # ultimo è allenatore  
                    colonne = riga.find_all('td')
                    if len(colonne) >= 2: #almeno due colonne
                        # prima colonna: nome giocarore:
                        nome_giocatore = colonne[0].select_one('a.player-name.player-link span').get_text(strip=True)

                        # seconda colonna: voto giocatore:
                        voto_reale_giocatore = colonne[1].select_one('span.player-grade').get('data-value').strip() 
                        voto_giocatore = colonne[1].select_one('span.player-fanta-grade').get('data-value').strip()
                        if voto_giocatore == '55': # S.V
                            voto_giocatore = '-1'
                        voto_reale_giocatore_clean = voto_reale_giocatore.replace(',','.')
                        voto_giocatore_clean = voto_giocatore.replace(',','.')
                        grades_list.append({'squad_name': squad_name, 'player_surname': nome_giocatore, 'grade': voto_reale_giocatore_clean, 'fanta_grade': voto_giocatore_clean})
        
            return grades_list
        else:
            print(f"Errore nella richiesta: {response.status_code}")

