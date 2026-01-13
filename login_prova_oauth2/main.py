from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from db import create_db_and_tables
from models import User
from auth import router as auth_router
from dependency import get_current_user

app = FastAPI()

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()

# Tutte le route di autenticazione saranno sotto /auth
app.include_router(auth_router, prefix="/auth")



@app.get("/home")    # Non serve per autenticazione ma solo per proteggere la route, da usare per le prossime API
async def access(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
    }



