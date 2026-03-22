from fastapi import FastAPI, Header, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
from jose import JWTError, jwt
from datetime import datetime, timezone
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import hashlib, json, sys
sys.path.insert(0, '/home/reiner/poc-stride-electoral')
from src.signing import generate_keypair, verify_signature
from src.audit import append_log
from cryptography.hazmat.primitives import serialization

app = FastAPI(title="Electoral Transmission API - Secure")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

SECRET_KEY = "chave-secreta-poc-stride-2026"
ALGORITHM = "HS256"
VALID_AUDIENCE = "electoral-api"

PRIVATE_KEY, PUBLIC_KEY = generate_keypair()

db = {}

class ResultPayload(BaseModel):
    id: str
    station_id: str
    timestamp: str
    candidates: dict
    hash: str
    signature: Optional[str] = None

def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        append_log("auth_failed", {"reason": "Token ausente ou malformado"}, actor="anonymous")
        raise HTTPException(status_code=401, detail="Token ausente ou malformado")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience=VALID_AUDIENCE)
        return payload
    except JWTError as e:
        append_log("auth_failed", {"reason": str(e)}, actor="anonymous")
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")

def verify_hash(payload: ResultPayload):
    content = {
        "id": payload.id,
        "station_id": payload.station_id,
        "timestamp": payload.timestamp,
        "candidates": payload.candidates
    }
    expected_hash = hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()
    if expected_hash != payload.hash:
        append_log("integrity_failed", {"reason": "Hash inválido", "station_id": payload.station_id}, actor="unknown")
        raise HTTPException(status_code=422, detail="Hash inválido — integridade comprometida")

def verify_sig(payload: ResultPayload):
    if not payload.signature:
        append_log("integrity_failed", {"reason": "Assinatura ausente", "station_id": payload.station_id}, actor="unknown")
        raise HTTPException(status_code=422, detail="Assinatura digital ausente")
    content = {
        "id": payload.id,
        "station_id": payload.station_id,
        "timestamp": payload.timestamp,
        "candidates": payload.candidates
    }
    if not verify_signature(content, payload.signature, PUBLIC_KEY):
        append_log("integrity_failed", {"reason": "Assinatura inválida", "station_id": payload.station_id}, actor="unknown")
        raise HTTPException(status_code=422, detail="Assinatura digital inválida — integridade comprometida")

@app.post("/upload")
@limiter.limit("60/minute")
async def upload_result(request: Request, payload: ResultPayload, claims=Depends(verify_token)):
    verify_hash(payload)
    verify_sig(payload)
    db[payload.id] = payload.dict()
    append_log("upload_success", {
        "result_id": payload.id,
        "station_id": payload.station_id
    }, actor=claims.get("sub", "unknown"))
    return {"status": "accepted", "id": payload.id, "operator": claims.get("sub")}

@app.get("/results/{result_id}")
async def get_result(result_id: str, authorization: Optional[str] = Header(None)):
    actor = "anonymous"
    if authorization and authorization.startswith("Bearer "):
        try:
            token = authorization.split(" ")[1]
            claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience=VALID_AUDIENCE)
            actor = claims.get("sub", "unknown")
        except Exception:
            pass
    append_log("query", {"result_id": result_id}, actor=actor)
    if result_id in db:
        return db[result_id]
    return {"error": "not found"}

@app.get("/health")
async def health(request: Request):
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/public-key")
async def get_public_key():
    pem = PUBLIC_KEY.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return {"public_key": pem.decode()}
