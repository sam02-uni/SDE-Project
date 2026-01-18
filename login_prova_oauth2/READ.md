# Auth Service 

Il servizio gestisce:
- Autenticazione OAuth2 con Google
- Emissione e validazione di Access Token (JWT)
- Gestione dei Refresh Token
- Sessione utente tramite cookie HTTP-only

---

## Tecnologie utilizzate

- FastAPI
- OAuth2 (Google)
- JWT (HS256)
- Cookie HTTP-only
- Microservizi REST
- Python, httpx, requests

---

## Flusso di autenticazione

### 1. Login con Google
- L’utente accede a `/auth/login`
- Viene reindirizzato a Google OAuth2
- Google ritorna a `/auth/callback`

### 2. Callback OAuth
Il servizio:
1. Scambia il `code` con Google per un `id_token`
2. Valida la firma RS256 usando le chiavi pubbliche Google (JWKS)
3. Recupera o crea l’utente nel `fanta-data-service`
4. Genera:
   - **Access Token JWT** (10 minuti)
   - **Refresh Token** (30 giorni)
5. Imposta i cookie:
   - `access_token` (HttpOnly)
   - `refresh_token` (HttpOnly)
6. Reindirizza l’utente alla home page

---

## Gestione dei token

### Access Token
- JWT firmato HS256
- Durata breve (10 minuti)
- Usato dai microservizi per autorizzare le richieste

### Refresh Token
- Token casuale sicuro
- Salvato nel `fanta-data-service`
- Inviato solo tramite cookie HTTP-only
- Usato esclusivamente dall’Auth Service

---

## Flusso di Refresh 

1. Il browser chiama un microservizio Fanta
2. Il microservizio risponde `401 Unauthorized` (token scaduto)
3. Il frontend intercetta il `401`
4. Il frontend chiama `/auth/refresh`
5. L’Auth Service:
   - Valida il refresh token
   - Genera un nuovo access token
   - Imposta un nuovo cookie `access_token`
6. Il frontend ripete automaticamente la richiesta originale (al microservizio fanta)

👉 I microservizi non gestiscono il refresh

---

## Endpoint principali

### `GET /auth/login`
Avvia il flusso OAuth2 con Google.

---

### `GET /auth/callback`
Gestisce il ritorno da Google, crea la sessione e imposta i cookie.

---

### `POST /auth/refresh`
Rigenera l’Access Token usando il Refresh Token presente nei cookie.

**Input**
- Cookie: `refresh_token`

**Output**
- Set-Cookie: `access_token`
- JSON di conferma

---

### `POST /auth/logout`
Revoca il refresh token e rimuove i cookie dal browser.

---

### `GET /auth/verify`
Valida un Access Token JWT.

**Uso**
- Endpoint chiamato dagli altri microservizi per autorizzare richieste.

**Header**
