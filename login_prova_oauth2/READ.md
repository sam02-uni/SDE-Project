# Servizio di Autenticazione – Fantacalcio

## Descrizione

Questo servizio implementa l’autenticazione degli utenti per l’applicazione Fantacalcio.
Supporta login tramite **Google OAuth 2.0**, gestione di **JWT (access token)** e **refresh token**.


## Tecnologie utilizzate

* Python 3.11
* FastAPI
* SQLModel
* PostgreSQL
* Google OAuth 2.0
* JWT (RS256)
* Docker

## Flusso di autenticazione (Google OAuth)

1. Il frontend richiede `/auth/login`
2. Il backend redireziona l’utente verso Google
3. Google restituisce un `code` al backend (`/auth/callback`)
4. Il backend scambia il `code` con:

   * `id_token`
   * `access_token`
5. Il backend verifica:

   * firma JWT
   * issuer
   * audience
6. Se l’utente non esiste, viene creato
7. Vengono restituiti:

   * access token
   * refresh token

---

## API principali

### Login

`GET /auth/login`

Redireziona l’utente alla pagina di login Google.

---

### Callback OAuth

`GET /auth/callback?code=...`

Gestisce il callback di Google e completa l’autenticazione.

---

### Logout

`POST /auth/logout`

**Body JSON:**

```json
{
  "refresh_token": "string"
}
```

Invalida il refresh token salvato.

---

## Autenticazione

* Access token: JWT
* Refresh token: salvato su database
* Autenticazione tramite header:

```
Authorization: Bearer <access_token>
```

---

## Avvio del progetto (locale)

```bash
docker compose up --build
```

Il servizio sarà disponibile su:

```
http://localhost:8000
```

