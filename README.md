# AegisSphere

**A Low-Latency, Serverless GenAI Orchestrator for Multi-Jurisdictional Operations and Sustainable Fan Experiences at the FIFA World Cup 2026**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Pydantic AI](https://img.shields.io/badge/Pydantic_AI-Gemini_Flash-purple.svg)](https://ai.pydantic.dev)
[![WCAG 2.1 AA](https://img.shields.io/badge/WCAG-2.1_AA-orange.svg)](https://www.w3.org/WAI/WCAG21/quickref/)

---

## Overview

AegisSphere is a serverless, GenAI-enabled orchestrator designed to manage real-time stadium operations across the 16 host venues of the FIFA World Cup 2026 in the **United States**, **Canada**, and **Mexico**.

### Key Capabilities

- 🛡️ **Crowd Safety Engine** — DIM-ICE framework with automated density/flow monitoring
- 🚇 **Accessible Transit Routing** — Step-free routes for 10+ venues with carbon scoring
- 📦 **Supply Chain Monitor** — Demand forecasting and cold chain temperature alerts
- 🌐 **Multilingual Translation** — 10 languages with pre-translated safety templates
- 🔐 **Defensive Security** — Prompt injection detection, PII filtering, output verification
- ♿ **WCAG 2.1 AA Dashboard** — Fully accessible operational command interface

---

## Architecture

```
                      +-----------------------+
                      |   HTTP Client Request  |
                      +-----------+-----------+
                                  |
                                  v
                      +-----------+-----------+
                      |   API Gateway Router  |
                      +-----------+-----------+
                                  |
                                  v
  +------------------+  +-----------+-----------+  +-------------------+
  |  Input Guardrail +->| FastAPI Lambda Engine |<->|  Pydantic AI Core |
  +------------------+  +-----------+-----------+  +---------+---------+
                                  ^                          |
                                  |                          v
                      +-----------+-----------+      +-------+-------+
                      |   Knowledge Base (JSON)|      |  Gemini 2.0   |
                      +------------------------+      |  Flash Agent  |
                                                      +---------------+
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
cd backend
pip install -r requirements.txt
```

### Run the Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

The API documentation is available at: [http://localhost:8000/docs](http://localhost:8000/docs)

### Run the Frontend

Open `frontend/index.html` in your browser. The dashboard connects to the backend at `localhost:8000`.

### Run Tests

```bash
cd backend
python -m pytest tests/ -v
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/health` | System health check |
| `POST` | `/v1/ops/evaluate` | Crowd safety evaluation (deterministic) |
| `POST` | `/v1/ops/evaluate/ai` | AI-enhanced safety evaluation (Gemini) |
| `POST` | `/v1/ops/transit` | Accessibility-aware transit routing |
| `POST` | `/v1/ops/supply` | Supply chain status and alerts |
| `POST` | `/v1/ops/translate` | Multilingual translation |
| `GET` | `/v1/ops/languages` | List supported languages |
| `GET` | `/v1/venues` | List all 16 host venues |
| `GET` | `/v1/venues/{city}` | Get specific venue profile |
| `POST` | `/v1/ops/query` | Guardrail-protected operational query |

---

## Safety Thresholds

| Condition | Escalation | Trigger |
|-----------|-----------|---------|
| D > 4.5 AND F < 25 | 🔴 RED | Immediate DIM-ICE intervention |
| D > 3.5 OR F < 35 | 🟡 AMBER | Heightened monitoring |
| Otherwise | 🟢 GREEN | Nominal operations |

Where D = crowd density (persons/m²) and F = pedestrian flow rate (persons/m/min).

---

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── schemas.py           # Pydantic data models
│   │   ├── agent.py             # Pydantic AI + Gemini agent
│   │   ├── crowd_safety.py      # DIM-ICE crowd safety engine
│   │   ├── guardrails.py        # Security guardrail pipeline
│   │   ├── transit_routing.py   # Accessible transit routing
│   │   ├── supply_chain.py      # Supply chain logistics
│   │   ├── multilingual.py      # Translation engine
│   │   ├── venue_data.py        # 16 venue profiles
│   │   └── knowledge_loader.py  # JSON knowledge base loader
│   ├── knowledge/               # JSON data files
│   ├── tests/                   # pytest test suite
│   └── requirements.txt
├── frontend/
│   ├── index.html               # Operations dashboard
│   ├── css/styles.css           # WCAG 2.1 AA design system
│   └── js/app.js                # Dashboard application logic
├── .gitignore
└── README.md
```

---

## Security

- **Input Guardrails**: 7 regex-based threat pattern detectors
- **Output Verification**: PII scanning + system prompt leakage prevention
- **RAG Quarantine**: Untrusted retrieved content is sanitized before model consumption
- **Domain Boundary**: Queries outside stadium operations are politely refused
- **Dual-LLM Pattern**: Planner (trusted) + Executor (quarantined) isolation

---

## Accessibility (WCAG 2.1 AA)

| Criterion | Implementation |
|-----------|---------------|
| 1.4.3 Contrast | 4.5:1 minimum on all text |
| 1.4.4 Resize | rem/em units for 200% scaling |
| 2.1.1 Keyboard | Full keyboard navigation |
| 2.4.7 Focus | 3px visible focus indicators |
| 3.1.2 Language | Dynamic `lang` attribute on translations |

---

## License

Built for the FIFA World Cup 2026 Hackathon. All rights reserved.
