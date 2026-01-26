from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from .auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configurazione CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8013"], # L'URL esatto del tuo frontend
    allow_credentials=True,                  # FONDAMENTALE per i cookie
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="login_prova_oauth2/static"), name="static")
# Tutte le route di autenticazione saranno sotto /auth

app.include_router(auth_router)





