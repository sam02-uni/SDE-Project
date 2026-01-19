from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from .models import User
from .auth import router as auth_router
from .dependency import get_current_user

app = FastAPI()


app.mount("/static", StaticFiles(directory="login_prova_oauth2/static"), name="static")
# Tutte le route di autenticazione saranno sotto /auth

app.include_router(auth_router)





