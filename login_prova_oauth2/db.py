import os
from sqlmodel import SQLModel, Field, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
from models import User, RefreshToken

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@db:5432/login_db")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

# Funzione per creare tutte le tabelle
async def create_db_and_tables():
    async with engine.begin() as conn:
        # Creiamo tutte le tabelle definite con SQLModel
        await conn.run_sync(SQLModel.metadata.create_all)


# Funzioni async per utenti
async def get_user(email: str):
    async for session in get_session():
        result = await session.exec(select(User).where(User.email == email))
        return result.first()

async def get_user_by_id(user_id: int):
    async for session in get_session():
        result = await session.exec(select(User).where(User.id == user_id))
        return result.first()

async def create_user(email: str, name: str, google_id: str):
    async for session in get_session():
        user = User(email=email, name=name, google_id=google_id)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

# Funzioni async per refresh token
async def save_refresh_token(user_id: int, token: str, expires_at: datetime):
    async for session in get_session():
        # Controllo se esiste già un refresh token per questo utente e lo elimino
        result = await session.exec(select(RefreshToken).where(RefreshToken.user_id == user_id))
        existing_token = result.first()
        if existing_token:
            await session.delete(existing_token)
            await session.commit()

        refresh_token = RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
        session.add(refresh_token)
        await session.commit()
        await session.refresh(refresh_token)
        return refresh_token

async def get_refresh_token(token: str):
    async for session in get_session():
        result = await session.exec(select(RefreshToken).where(RefreshToken.token == token))
        return result.first()
    
async def delete_ref_token(token: str):
    async for session in get_session():
        result = await session.exec(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        token_obj = result.first()
        if token_obj:
            await session.delete(token_obj)
            await session.commit()
