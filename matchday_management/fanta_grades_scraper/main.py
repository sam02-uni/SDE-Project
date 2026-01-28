from fastapi import FastAPI, HTTPException
from GradesScraper import GradesScraper
from typing import Optional

app = FastAPI(title="Fanta Grades Scraper Service", root_path="/scraper/fanta_grades")
gradeScraper = GradesScraper()

@app.get("/")
def read_root():
    return {"message": "Fanta Grades Scraper Service is running"}


@app.get("/scrape_grades/{matchday_number}")
def scrape_fanta_grades(matchday_number: Optional[int] = None):
    # TODO vedere per matchday different: 2025-26/{matchday_number}
    grades = gradeScraper.scrape_grades()
    if not grades:
        raise HTTPException(status_code=500, detail="Error scraping grades")        
    
    return {"matchday": matchday_number, "grades": grades}
