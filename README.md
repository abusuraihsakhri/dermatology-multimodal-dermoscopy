# Dermatology Multimodal Dermoscopy

> **Domain:** Clinical Decision Support & Biomedical Computing
> **Reference Guidelines & Standards:** CAP / CLSI / ISO Standards, ISIC Dermoscopy Challenge Standards

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Dermatology Multimodal Dermoscopy is an enterprise-grade clinical decision support platform that orchestrates multi-agent AI workers to evaluate dermoscopic and clinical data. It performs risk classification, protocol conformance checking, and safety escalation with cryptographic audit trail integrity.

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Multi-Agent Worker Orchestration**: Specialized workers (InvariantQC, SafetyEscalation, ProtocolConformance) evaluate tasks independently
- **Deterministic Calculation Engine**: Strict compliance with standard reference formulations and thresholds
- **Risk & Urgency Classification**: Multi-tier categorization (ROUTINE, ELEVATED_RISK, CRITICAL_STAT_PANIC) with automated action recommendations
- **Zero-PHI Outbound Guard**: AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers
- **HMAC-SHA256 Audit Trail**: Chained, cryptographically signed logs for every evaluation and state transition
- **FastAPI REST API**: OpenAPI 3.1 endpoints for audit, chat, and metrics
- **Prometheus Telemetry**: Operational metrics exporter
- **Active Learning Calibration**: Bayesian worker reliability weight tracking

---

## 🏗️ Project Structure

```
├── agents/                      # Core enterprise agent framework
│   ├── __init__.py
│   ├── api.py                   # FastAPI REST server
│   ├── base.py                  # PHI Guard, Audit Trail, Security
│   ├── learning.py              # Bayesian calibration engine
│   ├── llm_factory.py           # LLM provider abstraction
│   ├── metrics.py               # Prometheus metrics collector
│   ├── models.py                # Pydantic v2 data schemas
│   ├── streamer.py              # WebSocket telemetry broadcaster
│   ├── supervisor.py            # Master orchestrator
│   └── workers.py               # Specialized worker agents
├── derma_vision_ai/             # Frontier dual-modality fusion agent
│   ├── __init__.py
│   ├── agents.py                # Sub-agents and coordinator
│   ├── cli.py                   # Frontier CLI
│   ├── engine.py                # Core algorithmic engine
│   ├── models.py                # Frontier data models
│   └── server.py                # Frontier FastAPI server
├── tests/                       # Pytest test suite
├── cli.py                       # Main CLI entry point
├── derma_vision_ai_app.py       # Alternative entry point
├── enrichment.py                # Domain enrichment agents (ISIC, RCM, TBP, etc.)
├── simulator.py                 # High-throughput stress testing
├── pyproject.toml               # Package manifest
├── Dockerfile                   # Container build
└── docker-compose.yml           # Container orchestration
```

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/dermatology-multimodal-dermoscopy.git
cd dermatology-multimodal-dermoscopy

# Install dependencies
pip install fastapi uvicorn pydantic pytest

# For Docker deployment
cp .env.example .env
# Edit .env and set AUDIT_SECRET_KEY
docker-compose up --build
```

---

## 💻 CLI Quickstart & Usage

### 1. Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Supervisory Chat
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
| Parameter | Description | Default |
|:----------|:------------|:--------|
| `--task-id` | Unique task/case identifier | TASK-2026-001 |
| `--target` | Entity or patient key | KEY-TARGET-01 |
| `--primary` | Primary measurement/score | 28.5 |
| `--secondary` | Secondary kinetic/confidence score | 14.2 |
| `--critical` | Emergency escalation flag | False |
| `--status` | Status code/phenotype descriptor | DISCORDANT |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, DOBs, and patient names.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Audit Secret Key:** Configurable via `AUDIT_SECRET_KEY` environment variable. A random ephemeral key is generated at runtime if not set (with a warning).
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances, Claude, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring calibration drift.

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
# Build and run with Docker Compose
cp .env.example .env
# Set AUDIT_SECRET_KEY in .env
docker-compose up --build

# Or use Docker directly
docker build -t dermatology-multimodal-dermoscopy .
docker run -p 8000:8000 --env AUDIT_SECRET_KEY=your-secret-key dermatology-multimodal-dermoscopy
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
