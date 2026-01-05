from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import httpx
import os
from jose import jwt
import db

app = FastAPI()
load_dotenv()  # legge il file .env e carica le variabili in os.environ

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
SECRET_KEY = os.getenv("SECRET_KEY")  # per i JWT interni
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"

SCOPES = "openid email profile"


@app.get("/login")
def login():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": SCOPES,
        "redirect_uri": REDIRECT_URI,
        "access_type": "offline",
        "prompt": "consent"
    }
    url = httpx.URL(GOOGLE_AUTH_URL, params=params)
    print("Login URLj =", url)
    return RedirectResponse(url)

@app.get("/auth/callback")
async def auth_callback(code: str):
    async with httpx.AsyncClient() as client:
        #Scambio il code con token
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
            return {"error": "Google token request failed", "details": token_resp.text}
        token_data = token_resp.json()
        id_token = token_data.get("id_token")

        # Decodifico id_token Google
        user_info = jwt.get_unverified_claims(id_token)
        email = user_info.get("email")
        name = user_info.get("name")
        print(email)

        # Controllo se l'utente esiste nel DB (DA FARE)
       # user = await db.get_user(email)  # esempio funzione async
       # if not user:
            # registrazione: creo l'utente nel DB
        #    user = await db.create_user(
          #      email=email,
          #      name=name,
           #     google_id=user_info.get("sub")  # ID univoco Google
           # )

        # 4. Creo il JWT interno per il microservizio
        internal_jwt = jwt.encode({"user_id": 21, "email": email}, SECRET_KEY, algorithm="HS256") # da cambiare l'user id 

    return {"access_token": internal_jwt, "user": user_info}