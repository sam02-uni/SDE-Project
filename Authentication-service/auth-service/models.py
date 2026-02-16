from typing import List
from pydantic import BaseModel

class RefreshResponse(BaseModel):
    access_token: str
    message: str

class JWK(BaseModel):
    kty: str
    kid: str
    use: str
    alg: str
    n: str
    e: str

class JWKSResponse(BaseModel):
    keys: List[JWK]