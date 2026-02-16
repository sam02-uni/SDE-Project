from typing import List
from pydantic import BaseModel

class SignRequest(BaseModel):
    email: str
    name: str

class Token(BaseModel):
    token_str: str

class NewTokens(BaseModel):
    access_token: str
    refresh_token: str

class JWK(BaseModel):
    kty: str
    kid: str
    use: str
    alg: str
    n: str
    e: str

class JWKSResponse(BaseModel):
    keys: List[JWK]

class StatusResponse(BaseModel):
    status: str