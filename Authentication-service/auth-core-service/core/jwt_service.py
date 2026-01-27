from datetime import datetime, timedelta
from jose import jwt
from .keys import PRIVATE_KEY, PUBLIC_KEY, KID

def sign_token(user_id: int, email: str, minutes_valid: int ):
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=minutes_valid)
    }
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256", headers={"kid": KID})
    return token

def verify_token(token: str):
    return jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
