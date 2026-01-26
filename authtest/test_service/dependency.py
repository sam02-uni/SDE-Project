from fastapi import FastAPI, Request, Depends, HTTPException, Header
import httpx
from jose import jwt, JWTError
from datetime import datetime

app = FastAPI(title="Business Service")
AUTH_SERVICE_URL = "http://fanta-auth-service:8000/auth"


async def get_public_key(kid: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{AUTH_SERVICE_URL}/jwks")
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Impossibile recuperare JWKS")
        jwks = resp.json()
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return key
    raise HTTPException(status_code=401, detail="Chiave pubblica non trovata")

async def verify_token(authorization: str = Header(...)):
   
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token mancante o malformato")
    
    access_token = authorization.split(" ")[1]  # prendi solo il token dopo "Bearer "

    unverified_header = jwt.get_unverified_header(access_token)
    kid = unverified_header.get("kid")
    if not kid:
        raise HTTPException(status_code=401, detail="Token senza kid")

    public_key_jwk = await get_public_key(kid)

    try:
        payload = jwt.decode(
            access_token,
            public_key_jwk,
            algorithms=["RS256"],
        )

        
    except JWTError as e:
        print(str(e))
        raise HTTPException(status_code=401, detail=f"Token non valido: {str(e)}")

    if datetime.utcnow().timestamp() > payload.get("exp", 0):
        raise HTTPException(status_code=401, detail="Token scaduto")

    return payload
