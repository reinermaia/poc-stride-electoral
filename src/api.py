from fastapi import FastAPI, Header
from pydantic import BaseModel
from typing import Optional
import json, hashlib, uuid
from datetime import datetime, timezone

app = FastAPI(title="Electoral Transmission API - Baseline")

db = {}  # simula persistência em memória

class ResultPayload(BaseModel):
    id: str
    station_id: str
    timestamp: str
    candidates: dict
    hash: str

@app.post("/upload")
async def upload_result(payload: ResultPayload, authorization: Optional[str] = Header(None)):
    # baseline: sem validação de token, sem verificação de hash
    db[payload.id] = payload.dict()
    return {"status": "accepted", "id": payload.id}

@app.get("/results/{result_id}")
async def get_result(result_id: str):
    if result_id in db:
        return db[result_id]
    return {"error": "not found"}

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}
