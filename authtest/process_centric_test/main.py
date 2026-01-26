from fastapi import FastAPI, Depends, HTTPException, Request
import httpx
from fastapi.staticfiles import StaticFiles
from dependency import get_access_token, refresh_access_token

app = FastAPI(title="Process Centric")

BUSINESS_SERVICE_URL = "http://test-service:8000"
AUTH_SERVICE_URL="http://auth-service:8000/auth"

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/home")
async def get_dashboard_data(request: Request):
    #  Recupero l'access token 
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token mancante")
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{BUSINESS_SERVICE_URL}/compute",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
    if resp.status_code == 401:
        raise HTTPException(status_code=401, detail="Token non valido")

    return resp.json()