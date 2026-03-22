# POC — Empirical Validation of STRIDE Threat Catalog
## Electoral Results Transmission in Electronic Voting Systems

[![Python](https://img.shields.io/badge/Python-3.12.3-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135.1-green)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## Overview

This repository contains the proof-of-concept (POC) implementation developed
to empirically validate the STRIDE-based threat catalog proposed in the
scientific article:

> **"Threat Modeling in the Results Transmission Phase of Electronic Elections
> Using STRIDE"**

The POC simulates a realistic electoral results transmission pipeline and
injects representative attacks for each STRIDE category, measuring the
effectiveness of proposed security controls with quantitative metrics.

---

## Scientific Context

The article was evaluated by reviewers who identified the following limitation:

> *"Absence of empirical validation (experiments, simulation, or applied case study)"*

This POC directly addresses that limitation by providing:
- A controlled simulation environment with explicit trust boundaries
- Attack injection scripts for 5 STRIDE categories
- Quantitative metrics: detection rate, latency overhead, and resilience
- Reproducible results for independent verification

---

## Architecture
```
[ResultGenerator] → [TransmissionClient] → [APIGateway/FastAPI]
                                                    ↓
                                          [ValidationService]
                                                    ↓
                                   ┌────────────────┴───────────────┐
                             [MinIO/S3]           [Redis Queue]
                                   ↓                     ↓
                          [MetadataDB/PostgreSQL] [EventProcessor]
                                   └─────────────────────┘
                                                 ↓
                                         [AuditLogger]
```

### Trust Boundaries
- **TB-1**: ResultGenerator → TransmissionClient (local/source environment)
- **TB-2**: TransmissionClient → API Gateway (network crossing)
- **TB-3**: API Gateway → Cloud Services (managed services boundary)

---

## Attack Scenarios

| Scenario | STRIDE | Asset | Detection Rate | Overhead |
|---|---|---|---|---|
| Token Forgery | S — Spoofing | JWT credentials | 100% | +0.68ms |
| File Tampering | T — Tampering | Results file | 100% | +0.11ms |
| Pipeline Flooding | D — Denial of Service | API Gateway | — | +454.5% latency |
| Audit Log Tampering | R — Repudiation | Audit trails | 100% | qualitative |
| Pre-signed URL Leak | I — Info. Disclosure | Storage URL | 100% | qualitative |

---

## Repository Structure
```
poc-stride-electoral/
├── src/
│   ├── generator.py          # Simulates electoral result file generation
│   ├── api_secure.py         # FastAPI with all security controls
│   ├── signing.py            # RSA-2048 digital signature module
│   ├── audit.py              # Append-only chained hash audit log
│   ├── presigned.py          # Pre-signed URL with TTL and actor binding
│   └── token_generator.py    # JWT token generator for tests
├── attacks/
│   ├── attack_spoofing.py    # S — Token forgery attack
│   ├── attack_tampering.py   # T — File modification attack
│   ├── attack_dos.py         # D — Pipeline flooding attack
│   ├── attack_repudiation.py # R — Audit log tampering attack
│   └── attack_info_disclosure.py  # I — Pre-signed URL leak attack
├── tests/
│   ├── test_latency_spoofing.py   # Latency measurement (30 runs)
│   └── test_latency_tampering.py  # Latency measurement (30 runs)
├── data/
│   ├── resultado_spoofing.json
│   ├── resultado_tampering.json
│   ├── resultado_dos.json
│   ├── resultado_repudiation.json
│   ├── resultado_info_disclosure.json
│   ├── doc_spoofing.md
│   ├── doc_tampering.md
│   ├── doc_dos.md
│   ├── doc_repudiation.md
│   └── doc_info_disclosure.md
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## How to Reproduce

### Prerequisites
- Windows 10/11 with WSL2 enabled
- Docker Desktop (WSL2 integration enabled)
- Ubuntu 24.04 on WSL2

### Setup
```bash
# Clone the repository
git clone https://github.com/reinermaia/poc-stride-electoral.git
cd poc-stride-electoral

# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Create virtual environment and install dependencies
uv venv .venv
source .venv/bin/activate
uv pip install fastapi uvicorn python-jose[cryptography] \
               passlib[bcrypt] cryptography slowapi requests

# Start infrastructure
docker compose up -d
```

### Run the Experiments

**Terminal 1 — Start the API:**
```bash
source .venv/bin/activate
python3 -m uvicorn src.api_secure:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 — Run attack scenarios:**
```bash
source .venv/bin/activate
python3 attacks/attack_spoofing.py
python3 attacks/attack_tampering.py
python3 attacks/attack_dos.py
python3 attacks/attack_repudiation.py
python3 attacks/attack_info_disclosure.py
```

**Run latency tests:**
```bash
python3 tests/test_latency_spoofing.py
python3 tests/test_latency_tampering.py
```

---

## Key Scientific Finding

> SHA-256 hash alone is insufficient for integrity protection. An attacker
> who knows the algorithm can recompute the hash after tampering. RSA-2048
> digital signature is required to close this gap, as the attacker does not
> possess the private key.

---

## Environment

| Component | Version |
|---|---|
| OS | Ubuntu 24.04 LTS (WSL2) |
| Python | 3.12.3 |
| FastAPI | 0.135.1 |
| Docker | 28.5.1 |
| JWT Library | python-jose 3.5.0 |
| Crypto | RSA-2048 (cryptography) |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Citation

If you use this POC in your research, please cite the original article:
```
@article{stride-electoral-2026,
  title   = {Threat Modeling in the Results Transmission Phase of
             Electronic Elections Using STRIDE},
  author  = {[Authors]},
  year    = {2026}
}
```
