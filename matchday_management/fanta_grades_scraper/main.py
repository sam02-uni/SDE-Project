from fastapi import FastAPI, HTTPException
from GradesScraper import GradesScraper
from typing import Optional

app = FastAPI(title="Fanta Grades Scraper Service", root_path="/scraper/fanta_grades")
gradeScraper = GradesScraper()

mapping_players_fantacalcio_to_db = {
    'Ederson D.S.': 'Ederson',
    'Floriani Mussolini': 'floriani',
    'Malinovskyi': 'malinovskiy',
    'Esposito F.P.': 'Francesco Esposito',
    'Provstgaard':  'Oliver Nielsen',
    'Delprato': 'Del Prato',
    'Vitinha O.' : 'Vitinha',
    'Konè M.' : 'Kouadio Koné',
    'Thuram K.': 'Thuram-Ulie',
    'Al-Musrati' : 'Al Musrati',
    'Jashari': 'Jasari',
    'Djuric': 'Đurić',
    'Iling Junior': 'Iling-Junior',
    'Bella-Kotchap': 'Bella Kotchap',
    'Akpa Akpro': 'Akpa-Akpro'
}

@app.get("/")
def read_root():
    return {"message": "Fanta Grades Scraper Service is running"}


@app.get("/scrape_grades/{matchday_number}", summary = "Scrape the grades for the given matchday")
def scrape_fanta_grades(matchday_number: Optional[int] = None):
    
    grades = gradeScraper.scrape_grades(matchday_number=matchday_number)
    if not grades:
        raise HTTPException(status_code=500, detail="No grades found for this matchday. Error scraping grades")   
    
    # normalizzazione:
    for grade in grades:
        # mappa per nomi speciali:

        mappato = mapping_players_fantacalcio_to_db.get(grade['player_surname'])
        if mappato:
            grade['player_surname'] = mappato

        # rimuovi punti 
        grade['player_surname'] = grade['player_surname'].replace(".", "")
        

    return {"matchday": matchday_number, "grades": grades}
