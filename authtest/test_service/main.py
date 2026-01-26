from fastapi import FastAPI, Request, HTTPException, Depends 
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from dependency import verify_token

app = FastAPI()



app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/compute")
async def compute(user: dict = Depends(verify_token)):
    user_id = user["user_id"]

    # Qui puoi fare chiamate al data-service o logica business
    return {"user_id": user_id, "message": "Business logic eseguita correttamente"}
