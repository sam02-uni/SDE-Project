from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse
import os, requests
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from models import *

load_dotenv()

app = FastAPI(title="Auth Process Service")

HOME_URL="http://localhost:3000"

# Configurazione CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[HOME_URL], # L'URL esatto del tuo frontend
    allow_credentials=True,                  # FONDAMENTALE per i cookie
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
DATA_SERVICE_URL = "http://fanta-data-service:8000"
AUTH_CORE_URL = "http://auth-core-service:8000"  


GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"

SCOPES = "openid email profile"


jwks = requests.get(GOOGLE_JWKS_URL).json()

def get_google_public_key(kid: str):
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return key
    return None

@app.get("/auth/login", summary = "Initiates the delegated authentication flow")
def login():
    """
    Description: It generates the Google Consent URL and redirects the user to the official Google login page.

    """
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": SCOPES,
        "redirect_uri": REDIRECT_URI,
        "access_type": "offline",
        "prompt": "consent"
    }
    url = requests.Request("GET", GOOGLE_AUTH_URL, params=params).prepare().url
    return RedirectResponse(url)

@app.get("/auth/callback", summary = "Handles Google OAuth2 callback and issues internal tokens")
def auth_callback(code: str):
    """
    Description:
    It receives the code parameter returned by Google after the user grants consent,
    exchanges it for Google tokens (id_token and access_token), validates the id_token
    using Google's public keys, and creates/identifies the user in the Core Service.

    """
    #  Scambia code con token Google
    token_resp = requests.post(
        GOOGLE_TOKEN_URL,
        data={
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    if token_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Google token request failed")

    token_data = token_resp.json()
    id_token = token_data.get("id_token")

    id_token = token_data.get("id_token")
    access_token = token_data.get("access_token")

    unverified_header = jwt.get_unverified_header(id_token)
    kid = unverified_header.get("kid")
    if not kid:
        raise HTTPException(status_code=400, detail="Invalid ID token header")
        
    public_key = get_google_public_key(kid)
    if not public_key:
        raise HTTPException(status_code=400, detail="Public key not found")

    try:
        user_info = jwt.decode(
            id_token,
            public_key,
            algorithms=["RS256"],
            audience=CLIENT_ID,
            issuer=["accounts.google.com", "https://accounts.google.com"],
            access_token=access_token
        )
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid ID token: {str(e)}")
    
    payload = {
    "email": user_info.get("email"),
    "name": user_info.get("name")
    }

    response= requests.post(
        f"{AUTH_CORE_URL}/core/identify",
        json=payload
            )
    
    if response.status_code != 200:
        print(f"ERROR: {response.text}")
        raise HTTPException(status_code=response.status_code, detail="Errore in Core Service")
    
    data=response.json()
    internal_jwt = data["access_token"]
    refresh_token = data["refresh_token"]

    # 2. Gestione dei Cookie e Redirect (Responsabilità del Process Layer)
    redirect_url = f"{HOME_URL}/pages/home_news.html?token={internal_jwt}"
    response = RedirectResponse(url=redirect_url)
    
    cookie_params = {"httponly": True, "secure": False, "samesite": "lax", "path": "/"}
    response.set_cookie("refresh_token", refresh_token, max_age=60*60*24*30, **cookie_params)
    
    return response


@app.post("/auth/refresh",summary = "Renews an expired session using the refresh token cookie", response_model=RefreshResponse)
def refresh_token_endpoint(request: Request):
    """
    Description:
    Silent refresh endpoint used to renew an expired access token.
    The refresh token is retrieved from the `refresh_token` HttpOnly cookie
    and sent to the Core Service to generate a new internal access token.

    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token mancante")

    token_resp = requests.post(
        f"{AUTH_CORE_URL}/core/generate/access", 
        json={"token_str": refresh_token}
    )
    token_resp.raise_for_status()
    new_token = token_resp.json() 
    
    return {
        "access_token": new_token,
        "message": "Token rinnovato"
    }


@app.post("/auth/logout", summary = "Terminates the user session.")
def logout(request: Request):
    """
    Description:
    Terminates the user session by revoking the `refresh token` (if available)
    through the Core Service and clearing authentication cookies.
    
    """
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        try:
            payload={"token_str": refresh_token}
            response = requests.post(f"{AUTH_CORE_URL}/core/refresh/revoke", json=payload)
        except Exception:
            pass
    response = JSONResponse({"detail": "Logout effettuato con successo"})
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return response

@app.get("/auth/jwks", summary="Utility endpoint for public key distribution.", response_model=JWKSResponse)
def core_jwks():
    """
    Description:
    Utility endpoint used to expose the JSON Web Key Set (JWKS) required
    to verify JWT signatures issued by the Core Service.
    
    """
    return requests.get(f"{AUTH_CORE_URL}/core/jwks").json()

@app.delete("/remove/{email}") # PER TEST
def remove_user(email: str):
    # Gestione sessione manuale per operazioni bulk
    r1=requests.get(f"{DATA_SERVICE_URL}/users/by-email?user_email={email}")
    utente=r1.json()
    user_id=utente["id"]
    r= requests.delete(f"{DATA_SERVICE_URL}/users/{user_id}")
    if r.status_code==404:
        print ("NESSUNO ELIMINATO")
        return   
    
    print("UTENTE ELIMINATO")
    return

@app.get("/check_utenti") # PER TEST
def check_refresh():
    r= requests.get(f"{DATA_SERVICE_URL}/users")
    if r.status_code==404:
        print("NON CI SONO UTENTI")
        return
    
    users=r.json()
    stringa=""
    for u in users:
        stringa+=u["email"]+ " "
    return {"result" : stringa}