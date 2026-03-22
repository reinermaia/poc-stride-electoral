from jose import jwt
from datetime import datetime, timezone, timedelta

SECRET_KEY = "chave-secreta-poc-stride-2026"
ALGORITHM = "HS256"

def generate_token(subject: str, expires_in_minutes: int = 30) -> str:
    payload = {
        "sub": subject,
        "aud": "electoral-api",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

if __name__ == "__main__":
    token = generate_token("operador-zona-001")
    print(f"Token legítimo:\n{token}")
