from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.jwt_service import sign_token
from core.refresh_service import generate_refresh_token, token_expiry
from core.keys import KID, NUMBERS, b64
import requests

app = FastAPI(title="Auth Core Service",  root_path = "/core")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
DATA_SERVICE_URL = "http://fanta-data-service:8000"


# Request models
class SignRequest(BaseModel):
    user_id: int
    email: str
    minutes_valid: int

class VerifyRequest(BaseModel):
    token: str

# Endpoints

@app.post("/identify")
def core_identification(user_info: dict):

    email = user_info.get("email")
    name = user_info.get("name")

    # Controlla se l'utente esiste, altrimenti crea
    r = requests.get(f"{DATA_SERVICE_URL}/users/by-email?user_email={email}")
    if r.status_code == 404:
        r = requests.post(f"{DATA_SERVICE_URL}/users", json={"email": email, "username": name})
    r.raise_for_status()
    user = r.json()


    # Genera un internal jwt for the user
    internal_jwt = sign_token(user["id"], user["email"], 10)

    #  Chiede al business layer di generare refresh token
    token = generate_refresh_token()
    expiry = token_expiry().isoformat()

    #  Salva refresh token su data service
    requests.post(f"{DATA_SERVICE_URL}/refresh/save", json={
        "token": token,
        "user_id": user["id"],
        "expires_at": expiry
    })

    return {
        "access_token": internal_jwt,
        "refresh_token": token
    }

@app.post("/generate/access")
def core_session_user(token : dict):

    token_obj = requests.post(f"{DATA_SERVICE_URL}/refresh/get", json={"token": token["token"]})
    token_obj.raise_for_status()
    token_data = token_obj.json()
    
    # 2. Identico all'originale
    user_data = requests.get(f"{DATA_SERVICE_URL}/users/{token_data['user_id']}").json()
    new_token=sign_token(user_data['id'], user_data['email'], 10)
    
    # Restituisco l'intero oggetto user come faceva il data service
    return new_token

@app.get("/jwks")
def core_jwks():
    """
    Return the JSON Web Key Set (JWKS) containing the public keys used for JWT verification.

    Each key includes:
    - **kty**: key type (RSA)
    - **kid**: unique key ID
    - **use**: usage (sig)
    - **alg**: algorithm (RS256)
    - **n**: modulus in base64url
    - **e**: exponent in base64url
    """
    return {
        "keys": [{
            "kty": "RSA",
            "kid": KID,
            "use": "sig",
            "alg": "RS256",
            "n": b64(NUMBERS.n),
            "e": b64(NUMBERS.e)
        }]
    }
