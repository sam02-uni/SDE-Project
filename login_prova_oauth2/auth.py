from fastapi import APIRouter, HTTPException, Body, Cookie, Response, Request
from fastapi.responses import RedirectResponse, JSONResponse
from dotenv import load_dotenv
import httpx, os, secrets, requests
from jose import jwt, JWTError
from datetime import datetime, timedelta
from sqlmodel import select, Session
import requests



router = APIRouter(prefix="/auth", tags=["auth-service"])
load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

SECRET_KEY = os.getenv("SECRET_KEY")
DATA_SERVICE_URL = "http://fanta-data-service:8000"

SCOPES = "openid email profile"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"

# Richiesta sincrona per recuperare le chiavi pubbliche di Google all'avvio
jwks = requests.get(GOOGLE_JWKS_URL).json()

def get_google_public_key(kid: str):
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return key
    return None

@router.get("/login")
def login():
    """
ENDPOINT: GET /auth/login
DESCRIZIONE: Avvia il flusso OAuth2 reindirizzando l'utente verso Google.
SCOPES: openid, email, profile.
OUTPUT: Redirect alla pagina di login Google.
"""
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": SCOPES,
        "redirect_uri": REDIRECT_URI,
        "access_type": "offline",
        "prompt": "consent"
    }
    url = httpx.URL(GOOGLE_AUTH_URL, params=params)
    return RedirectResponse(url)

@router.get("/callback")
def auth_callback(code: str):
    """
ENDPOINT: GET /auth/callback
DESCRIZIONE: Gestisce il ritorno da Google, valida l'utente e crea la sessione.
INPUT: Query param 'code' fornito da Google.
LOGICA:
  1. Scambia 'code' con ID_Token tramite Google APIs.
  2. Verifica firma RS256 dell'ID_Token (Google JWKS).
  3. Sincronizza utente con 'fanta-data-service' (Login/Registrazione).
  4. Genera JWT interno (10 min) e Refresh Token (30 gg).
OUTPUT: 
  - Redirect alla Home Page.
  - Set-Cookie: access_token 
  - Set-Cookie: refresh_token 
"""
    # Utilizzo del client sincrono di httpx
    with httpx.Client() as client:
        token_resp = client.post(
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

        email = user_info.get("email")
        name = user_info.get("name")

# 1️⃣ Recupera o crea l'utente
        r = requests.get(f"{DATA_SERVICE_URL}/users/by-email/{email}")

        if r.status_code == 404:
            r = requests.post(
                f"{DATA_SERVICE_URL}/users",
                json={
                    "email": email,
                    "username": name,
                }
    )

        r.raise_for_status()
        user = r.json()   # ora è un dict, non un model SQLAlchemy

        # 2️⃣ Crea JWT interno
        internal_jwt = jwt.encode(
            {
                "user_id": user["id"],
                "email": user["email"],
                "exp": datetime.utcnow() + timedelta(minutes=10)
            },
        SECRET_KEY,
        algorithm="HS256"
)

# 3️⃣ Refresh token
        refresh_token = secrets.token_urlsafe(64)

        requests.post(
            f"{DATA_SERVICE_URL}/refresh/save",
            json={
                "user_id": user["id"],
                "refresh_token": refresh_token,
                "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
            }
        )

# 4️⃣ Redirect
        response = RedirectResponse(url="/static/home.html")

# 5️⃣ Cookie
        cookie_params = {
            "httponly": True,
            "secure": False,  # True in produzione HTTPS
            "samesite": "lax",
            "path": "/"
        }

        response.set_cookie(
            key="access_token",
            value=internal_jwt,
            max_age=600,
            **cookie_params
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=60 * 60 * 24 * 30,
            **cookie_params
)       

        return response

@router.post("/refresh")
def refresh_token_endpoint(request: Request):
    """
ENDPOINT: POST /auth/refresh
DESCRIZIONE: Rigenera l'Access Token scaduto utilizzando il Refresh Token.
INPUT: Cookie 'refresh_token'.
LOGICA:
  1. Recupera il Refresh Token dal 'fanta-data-service'.
  2. Verifica validità e data di scadenza (expires_at).
  3. Recupera dati utente associati.
  4. Genera un nuovo JWT interno (Access Token).
OUTPUT: 
  - Nuovo cookie 'access_token' (HttpOnly, 10 min).
  - JSON di conferma successo.
"""
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token mancante")

    token_obj = requests.get(f"{DATA_SERVICE_URL}/refresh/get/{refresh_token}")
    if not token_obj:
        raise HTTPException(status_code=401, detail="Refresh token non valido")

    token=token_obj.json()
    expires_at = datetime.fromisoformat(token["expires_at"])
    if expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token scaduto")

    user = requests.get(f"{DATA_SERVICE_URL}/users/{token['user_id']}")
    if not user:
        raise HTTPException(status_code=404, detail="Utente non trovato")

    utente=user.json()
    new_jwt = jwt.encode(
        {
            "user_id": utente["id"],
            "email": utente["email"],
            "exp": datetime.utcnow() + timedelta(minutes=10),
        },
        SECRET_KEY,
        algorithm="HS256"
    )
    
    response = JSONResponse(content={"message": "Token rinnovato con successo"})
    cookie_params = {
            "httponly": True,
            "secure": False,  # True in produzione HTTPS
            "samesite": "lax",
            "path": "/"
        }

    response.set_cookie(
        key="access_token",
        value=new_jwt,
        max_age=600,
        **cookie_params
        )


    return response

@router.post("/logout")
def logout(request: Request):
    """
ENDPOINT: POST /auth/logout
DESCRIZIONE: Termina la sessione dell'utente e pulisce i client.
INPUT: Cookie 'refresh_token'.
LOGICA:
  1. Invia richiesta di revoca (DELETE) del Refresh Token al 'fanta-data-service'.
  2. Rimuove forzatamente i cookie dal browser dell'utente.
OUTPUT: 
  - Rimozione cookie 'access_token' e 'refresh_token'.
  - JSON di conferma logout.
"""
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        try:
            requests.delete(f"{DATA_SERVICE_URL}/refresh/revoke/{refresh_token}")
        except Exception as e:
            # Anche se il data-service fallisce, procediamo a pulire i cookie
            print(f"Errore revoca token: {e}")

    # 2. Creiamo una risposta che "pulisce" i cookie nel browser
    response = JSONResponse(content={"detail": "Logout effettuato con successo"})
    
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    
    return response

@router.get("/verify")
def verify_token(request: Request):
    """
ENDPOINT: GET /auth/verify
DESCRIZIONE: Valida l'Access Token e restituisce l'identità dell'utente.
INPUT: Header 'Authorization: Bearer <JWT>'.
LOGICA:
  1. Estrae il token JWT dall'header Authorization.
  2. Decodifica e verifica la firma utilizzando la SECRET_KEY interna.
  3. Controlla la validità temporale (exp claim).
OUTPUT: 
  - JSON contenente 'id' (user_id) ed 'email' dell'utente autenticato.
SICUREZZA: 
  - Restituisce 401 se il token è manomesso, scaduto o mancante.
  - Utilizzato dagli altri microservizi per autorizzare le richieste.
"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Header mancante")
    
    token = auth_header.split(" ")[1]
    try:
        decoded_data = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=["HS256"]
        )


        return {
                "id": decoded_data.get("user_id"),
                "email": decoded_data.get("email")
            
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Token non valido o scaduto")



@router.delete("/remove/{email}") # PER TEST
def remove_user(email: str):
    # Gestione sessione manuale per operazioni bulk
    r1=requests.get(f"{DATA_SERVICE_URL}/users/by-email/{email}")
    utente=r1.json()
    user_id=utente["id"]
    r= requests.delete(f"{DATA_SERVICE_URL}/users/{user_id}")
    if r.status_code==404:
        print ("NESSUNO ELIMINATO")
        return   
    
    print("UTENTE ELIMINATO")
    return

@router.get("/check_utenti")
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
