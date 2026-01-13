from fastapi import APIRouter, HTTPException, Body, Cookie
from fastapi.responses import RedirectResponse, JSONResponse
from dotenv import load_dotenv
import httpx, os, secrets, requests
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
import db
from models import User, RefreshToken
from sqlmodel import select

router = APIRouter()
load_dotenv()  # legge il file .env e carica le variabili in os.environ

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
SECRET_KEY = os.getenv("SECRET_KEY")

SCOPES = "openid email profile"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
jwks = requests.get(GOOGLE_JWKS_URL).json()

# prendo la chiave pubblica che devo utilizzare per decodificare il token
def get_google_public_key(kid: str):
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return key
    return None


@router.get("/login")
def login():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code", # mi manda un codice temporaneo, non ancora il token
        "scope": SCOPES,
        "redirect_uri": REDIRECT_URI,
        "access_type": "offline",
        "prompt": "consent"
    }
    url = httpx.URL(GOOGLE_AUTH_URL, params=params)
    return RedirectResponse(url) # lo mando a google


@router.get("/callback")
async def auth_callback(code: str):
    async with httpx.AsyncClient() as client:  # sto creando il client asincrono pre richiedere il token da google 
        token_resp = await client.post(
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
        access_token= token_data.get("access_token")

        unverified_header = jwt.get_unverified_header(id_token)
        kid = unverified_header.get("kid")
        if not kid:
            raise HTTPException(status_code=400, detail="Invalid ID token header")
        public_key = get_google_public_key(kid)  # prendo la chiave pubblica da usare per verificare la firma
        if not public_key:
            raise HTTPException(status_code=400, detail="Public key not found")

        try:
            user_info = jwt.decode(
                id_token,
                public_key,
                algorithms=["RS256"],
                audience=CLIENT_ID,  #mi assicuro che il token è stato creato per la mia applicazione
                issuer=["accounts.google.com", "https://accounts.google.com"],
                access_token= access_token
            )
        except JWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid ID token: {str(e)}")

        email = user_info.get("email")
        name = user_info.get("name")

        user = await db.get_user(email)
        if not user:
            user = await db.create_user(email=email, name=name, google_id=user_info.get("sub"))

        internal_jwt = jwt.encode(
            {"user_id": user.id, "email": email, "exp": datetime.utcnow() + timedelta(minutes=10)},
            SECRET_KEY,
            algorithm="HS256"
        )
        refresh_token = secrets.token_urlsafe(64)
        await db.save_refresh_token(user.id, refresh_token, datetime.utcnow() + timedelta(days=30))
        # print(f"Refresh token: {refresh_token}")
        response = RedirectResponse(url="/static/home.html") 
        response.set_cookie(
            key="access_token",
            value=internal_jwt,
            httponly=True,
            secure=False,      # True in produzione con HTTPS
            samesite="lax",
            max_age=600,        # in secondi
            path="/"
)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=30*24*3600,
            path="/"
)
    return response
       
    #return {"access_token": internal_jwt, "refresh_token": refresh_token, "user": user_info}

@router.post("/refresh")
async def refresh_token(refresh_token: str = Body(..., embed=True)):
 
    # Controllo se il refresh token esiste e non è scaduto
    token_obj = await db.get_refresh_token(refresh_token)
    if not token_obj:
        raise HTTPException(status_code=401, detail="Refresh token non valido")
    now = datetime.utcnow()  # timezone-naive in UTC
    if token_obj.expires_at < now:
        raise HTTPException(status_code=401, detail="Refresh token scaduto, effettua di nuovo il login")
    # Prendo l'utente collegato al token
    user = await db.get_user_by_id(token_obj.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utente non trovato")

    # Creo nuovo access token JWT
    new_jwt = jwt.encode(
        {"user_id": user.id, "email": user.email, "exp": datetime.utcnow() + timedelta(minutes=10)},
        SECRET_KEY,
        algorithm="HS256"
    )
    
    return {"access_token": new_jwt}

@router.post("/logout")
async def logout(refresh_token : str = Body(..., embed=True)):
    token= await db.get_refresh_token(refresh_token)
    print(token)
    if token:
        await db.delete_ref_token(refresh_token)
    
    return ("Logout effettuato")

@router.delete("/remove")  #Solo per test
async def remove_all():
   
    async for session in db.get_session():
        # Elimino prima i refresh token
        result_tokens = await session.exec(select(RefreshToken))
        tokens = result_tokens.all()
        for t in tokens:
            await session.delete(t)
        await session.commit()

        # Elimino gli utenti
        result_users = await session.exec(select(User))
        users = result_users.all()
        for u in users:
            await session.delete(u)
        await session.commit()


    return {"detail": "Tutti gli utenti e refresh token sono stati rimossi"}

@router.get("/check_token/{token}")  #Solo per test
async def check_refresh(token: str):
    token_obj = await db.get_refresh_token(token)
    if not token_obj:
        return {"exists": False}
    return {"exists": True}

@router.get("/me")
async def get_me(access_token: str = Cookie(None), refresh_token : str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Non loggato")
    try:
        user_data = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
    except ExpiredSignatureError:
        # Token scaduto, provo con il refresh token
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Token scaduto, fai login")
        new_token = await db.refresh_access_token(refresh_token)  # logica simile a /refresh
        if not new_token:
            raise HTTPException(status_code=401, detail="Refresh token non valido")
        
    # Decodifica di nuovo il nuovo token
        user_data = jwt.decode(new_token, SECRET_KEY, algorithms=["HS256"])
        user = await db.get_user_by_id(user_data["user_id"])
        if not user:
            raise HTTPException(status_code=404, detail="Utente non trovato")
        response = JSONResponse({"id": user.id, "email": user.email, "name": user.name} )
        response.set_cookie(
            key="access_token",
            value=new_token,
            httponly=True,
            samesite="lax",
            max_age=600,
            path="/"
        )
      
        return response

    # Token valido
    user = await db.get_user_by_id(user_data["user_id"])
  
    if not user:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    
    return {"id": user.id, "email": user.email, "name": user.name}