import secrets
from datetime import datetime, timedelta

def generate_refresh_token():
    return secrets.token_urlsafe(64)

def token_expiry(days_valid: int = 30):
    return datetime.utcnow() + timedelta(days=days_valid)
