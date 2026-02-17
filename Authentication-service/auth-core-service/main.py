from fastapi import FastAPI, HTTPException
from core.jwt_service import sign_token
from core.refresh_service import generate_refresh_token, token_expiry
from core.keys import KID, NUMBERS, b64
import requests
from models import *


app = FastAPI(title="Auth Core Service",  root_path = "/core")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
DATA_SERVICE_URL = "http://fanta-data-service:8000"


@app.post("/identify", summary= "It generates the internal tokens", response_model=NewTokens)
def core_identification(user_info: SignRequest):
    """
    Description:
    It receives the user's name and email and queries the database to retrieve the user ID. 
    If the user does not exist, it creates a new record. Based on the gathered information, 
    it generates an access token along with a refresh token. 
    """
    email = user_info.email
    name = user_info.name

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

@app.post("/generate/access", summary="It generates a new access token from the refresh one", response_model=str)
def core_session_user(refresh_token : Token):
    """
    Description:
    Receives a refresh token, retrieves the associated user from the database, and issues a new access token.
 
    """
    token=refresh_token.token_str
    try:    
        payload={"token": token}
        token_obj = requests.post(f"{DATA_SERVICE_URL}/refresh/get", json=payload)
        token_data = token_obj.json()
        user_data = requests.get(f"{DATA_SERVICE_URL}/users/{token_data['user_id']}").json()
        new_token=sign_token(user_data['id'], user_data['email'], 10)
    except Exception as e:
        raise HTTPException(
            detail=f"Internal error in the access token generation: {str(e)}"
        )
    
    return new_token

@app.post("/refresh/revoke", summary="It revokes the refresh token", response_model=StatusResponse)
def core_revoke_refresh(refresh_token: Token):
    """
    Description:
    It revokes the refresh token associated to the user
    """
    token=refresh_token.token_str
    try:
        payload={"token": token}
        response = requests.post(f"{DATA_SERVICE_URL}/refresh/revoke", json=payload)
    except Exception as e:
        raise HTTPException(
            detail=f"Internal error in the refresh token revoking: {str(e)}"
        )

    return response.json()

@app.get("/jwks", summary="It returns the public key", response_model=JWKSResponse)
def core_jwks():
    """
    Return the JSON Web Key Set (JWKS) containing the public keys used for JWT verification.

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
