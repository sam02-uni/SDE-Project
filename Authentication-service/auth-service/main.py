from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse
import os, requests
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

app = FastAPI(title="Auth Process Service")


app.mount("/static", StaticFiles(directory="static"), name="static")

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
HOME_URL="http://localhost:8013"

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

SCOPES = "openid email profile"


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
    """
    Description: Post-login landing page that handles session creation and user identification.
    
    :param code: Authorization code to be exchanged for the Google access_token and id_token
    :type code: str
    :return: Redirect to the home page after setting internal access_token and refresh_token in the cookies.
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

    #  Recupera dati utente dal data service
    email = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", 
                         headers={"Authorization": f"Bearer {token_data['access_token']}"}
                        ).json().get("email")

    # Controlla se l'utente esiste, altrimenti crea
    r = requests.get(f"{DATA_SERVICE_URL}/users/by-email/{email}")
    if r.status_code == 404:
        r = requests.post(f"{DATA_SERVICE_URL}/users", json={"email": email})
    r.raise_for_status()
    user = r.json()

    #  Chiede al business layer di generare JWT interno
    core_resp = requests.post(f"{AUTH_CORE_URL}/core/sign", json={
        "user_id": user["id"],
        "email": user["email"],
        "minutes_valid" : 10
    })
   
    internal_jwt = core_resp.json()["token"]

    #  Chiede al business layer di generare refresh token
    refresh_resp = requests.post(f"{AUTH_CORE_URL}/core/refresh/generate")
    refresh_token = refresh_resp.json()["refresh_token"]

    #  Salva refresh token su data service
    requests.post(f"{DATA_SERVICE_URL}/refresh/save", json={
        "token": refresh_token,
        "user_id": user["id"],
        "expires_at": refresh_resp.json()["expires_at"]
    })

    #  Imposta cookie e redirect
    response = RedirectResponse(url=HOME_URL)
    cookie_params = {"httponly": True, "secure": False, "samesite": "lax", "path": "/"}
    response.set_cookie("access_token", internal_jwt, max_age=600, **cookie_params)
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

    response = JSONResponse({"message": "Token rinnovato con successo"})
    print("Token rinnovato con successo")
    cookie_params = {"httponly": True, "secure": False, "samesite": "lax", "path": "/"}
    response.set_cookie("access_token", new_jwt, max_age=600, **cookie_params)
    return response


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
            requests.delete(f"{DATA_SERVICE_URL}/refresh/revoke/{refresh_token}")
        except Exception:
            pass
    response = JSONResponse({"detail": "Logout effettuato con successo"})
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return response

@app.get("/jwks")
def core_jwks():
    """
    Description: Utility endpoint for public key distribution.
    
    :return: JSON with public key
    """
    return requests.get(f"{AUTH_CORE_URL}/core/jwks").json()

