from fastapi import Depends, HTTPException, Request, Response
import httpx

AUTH_SERVICE_URL="http://auth-service:8000/auth"

async def get_access_token(request: Request, response: Response) -> str:
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")

    if not access_token:
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Sessione mancante")

        async with httpx.AsyncClient() as client:
            refresh_resp = await client.post(
                f"{AUTH_SERVICE_URL}/refresh",
                cookies={"refresh_token": refresh_token}
            )

        if refresh_resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Refresh token non valido")

        access_token = refresh_resp.json().get("access_token")
        if not access_token:
            raise HTTPException(status_code=401, detail="Impossibile ottenere access token")

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="lax"
        )

    return access_token

async def refresh_access_token(refresh_token: str, response: Response) -> str:
    async with httpx.AsyncClient() as client:
        refresh_resp = await client.post(
            f"{AUTH_SERVICE_URL}/refresh",
            cookies={"refresh_token": refresh_token}
        )

    if refresh_resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Refresh token non valido o scaduto")

    new_access_token = refresh_resp.json().get("access_token")
    if not new_access_token:
        raise HTTPException(status_code=401, detail="Impossibile ottenere nuovo access token")

    # Aggiorniamo il cookie
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=600  # 10 minuti
    )

    return new_access_token