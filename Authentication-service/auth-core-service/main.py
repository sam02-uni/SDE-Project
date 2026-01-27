from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.jwt_service import sign_token, verify_token
from core.refresh_service import generate_refresh_token, token_expiry
from core.keys import KID, NUMBERS, b64

app = FastAPI(title="Auth Core Service")



# Request models
class SignRequest(BaseModel):
    user_id: int
    email: str
    minutes_valid: int

class VerifyRequest(BaseModel):
    token: str

# Endpoints

@app.post("/core/sign")
def core_sign(req: SignRequest):
    """
    Generates an internal JWT for the user.

    - **user_id**: The user's ID (string)
    - **email**: User's email
    - **minutes_valid**: Token expiration time in minutes

    Returns a JSON containing the signed token.
    """
    token = sign_token(req.user_id, req.email, req.minutes_valid)
    return {"token": token}

@app.post("/core/verify")
def core_verify(req: VerifyRequest):
    """
    Verify the provided JWT.

    - **token**: JWT string to be verified

    Returns whether the token is valid and the decoded payload if valid.
    """
    try:
        payload = verify_token(req.token)
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/core/refresh/generate")
def core_generate_refresh():
    token = generate_refresh_token()
    expiry = token_expiry()
    return {"refresh_token": token, "expires_at": expiry.isoformat()}

@app.get("/core/jwks")
def core_jwks():
    """
    Return the JSON Web Key Set (JWKS) containing the public keys used for JWT verification.

    Each key includes:
    - **kty**: key type (RSA)
    - **kid**: unique key ID
    - **use**: usage (sig)
    - **alg**: algorithm (RS256)
    - **n**: modulus in base64url
    - **e**: exponent in base64url
    """
    return {
        "keys": [{
            "kty": "RSA",
            "kid": KID,
            "use": "sig",
            "alg": "RS256",
            "n": b64(NUMBERS.n),
            "e": b64(NUMBERS.e)
        }]
    }
