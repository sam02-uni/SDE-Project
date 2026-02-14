from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse
import os, requests
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError


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

@app.get("/auth/login")
def login():
    """
    Description: Initiates the delegated authentication flow. It generates the Google Consent URL and redirects the user to the official Google login page.

    Response: 307 Temporary Redirect to the Google Authentication Server.
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

@app.get("/auth/callback")
def auth_callback(code: str):
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
    
    response= requests.post(
        f"{AUTH_CORE_URL}/core/identify",
        json=user_info
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


@app.post("/auth/refresh")
def refresh_token_endpoint(request: Request):
    """
    Description: Silent refresh endpoint to renew expired sessions.
    
    :param request: The incoming HTTP request containing the refresh_token cookie.
    :type request: Request
    :return: JSONResponse with a new access token set in the cookies.

    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token mancante")

    # Chiede al data service se il token è valido
    token_obj = requests.post(f"{DATA_SERVICE_URL}/refresh/get", json={"token": refresh_token})
    token_obj.raise_for_status()
    token = token_obj.json()
    user = requests.get(f"{DATA_SERVICE_URL}/users/{token['user_id']}").json()

    # Chiede al core layer di generare nuovo JWT
    new_jwt_resp = requests.post(f"{AUTH_CORE_URL}/core/sign", json={
        "user_id": user["id"],
        "email": user["email"],
        "minutes_valid": 10
    })
    new_jwt = new_jwt_resp.json()["token"]

    #response = JSONResponse({"message": "Token rinnovato con successo"})
    #cookie_params = {"httponly": True, "secure": False, "samesite": "lax", "path": "/"}
    #response.set_cookie("access_token", new_jwt, max_age=600, **cookie_params)
    return {
        "access_token": new_jwt,
        "message": "Token rinnovato"
    }


@app.post("/auth/logout")
def logout(request: Request):
    """
    Description: Terminates the user session.
    
    :param request: The incoming HTTP request containing the refresh_token and access_token cookie.
    :type request: Request
    :return: Delete cookie
    """
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        try:
            payload={"token": refresh_token}
            response = requests.post(f"{DATA_SERVICE_URL}/refresh/revoke", json=payload)
        except Exception:
            pass
    response = JSONResponse({"detail": "Logout effettuato con successo"})
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return response

@app.get("/auth/jwks")
def core_jwks():
    """
    Description: Utility endpoint for public key distribution.
    
    :return: JSON with public key
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