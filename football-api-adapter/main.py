# Adapter Service
# Questo servizio è un adapter per interfacciarsi con un'ipotetica Football API esterna
# Fornisce un'API REST per ottenere dati sui giocatori, squadre, partite


from fastapi import FastAPI


app = FastAPI(title="Football API Adapter")

#@app.get("/update_players") # Endpoint to update player data from external football API
#def update_players():