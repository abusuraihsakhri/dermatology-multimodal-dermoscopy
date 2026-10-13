# Dermatology Multimodal Dermoscopy

### [Open the Live Application →](https://abusuraihsakhri.github.io/dermatology-multimodal-dermoscopy/)

A **research software demonstration** of deterministic task-evaluation rules, CSV batch processing, and an in-memory HMAC-SHA256 event ledger. The repository also contains a standalone browser interface for exploring the same example rules.

**Important limitations:** Despite the project name, the current implementation does **not** ingest clinical or dermoscopic images, perform multimodal fusion, compute a validated seven-point dermoscopy score, classify melanoma, or provide diagnostic decision support. Its numeric thresholds (primary > 25; secondary > 12) and descriptor checks are example conditions without established clinical validity. The mock chat responder does not run a language model.

## Browser demonstration

A static, local-only numerical rule demonstration is available in [`web/`](web/). To run it locally:

```bash
cd web
python -m http.server 8001
# Open http://localhost:8001/
```

The browser interface evaluates the synthetic conditions in JavaScript and exports a JSON result. It does not use Python, upload inputs, load external analytics or models, or generate a cryptographic audit signature. **Do not enter patient or identifiable personal data.** The live GitHub Pages deployment is checked by an automated post-deployment HTTP smoke test for the published HTML and JavaScript module.

## Python setup

Requires Python 3.9 or newer. To install the package and API/test dependencies:

```bash
git clone https://github.com/abusuraihsakhri/dermatology-multimodal-dermoscopy.git
cd dermatology-multimodal-dermoscopy
python -m pip install -e ".[api,test]"
python -m pytest -q
```

The package exposes two entry points: `dermatology-multimodal-audit` (the `agents/` rule and ledger workflow) and `dermatology-multimodal-dermoscopy` (the legacy `derma_vision_ai/` rule workflow).

## CLI and API

```bash
# Main rule engine, using synthetic identifiers
python cli.py audit --task-id DEMO-001 --target SYNTH-001 --primary 28.5 --secondary 14.2
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit

# Local API server (not intended for public exposure)
python cli.py serve --host 127.0.0.1 --port 8000
```

On the FastAPI server, `GET /health` returns health metadata, `POST /api/audit` evaluates a structured numeric payload, `POST /api/chat` returns a mock response, and `GET /api/audit/logs` returns in-memory ledger metadata. Interactive API documentation is available at `/docs`. The alternate `derma_vision_ai/` package has a separate CLI and API schema.

## Security and data handling

The Python workflow screens some common identifiers with regular expressions, but **this is not comprehensive de-identification or a guarantee of HIPAA/GDPR compliance**. The API has no built-in authentication and maintains task dossiers in server memory. Do not send real patient information or expose the API on a public network without adding appropriate authentication, transport security, data governance, and independent security review.

The ledger signs each event using an HMAC-SHA256 key supplied through `AUDIT_SECRET_KEY`. It checks every signature and hash-chain link, but the ledger is **in-memory only**: records are lost on restart and are not a durable or independently anchored audit log. An ephemeral key is used when no key is configured. CSV outputs are written to local files. The browser demo stores no records persistently.

## Docker

```bash
cp .env.example .env
# Set AUDIT_SECRET_KEY to a fresh random value before starting
docker compose up --build
```

Docker Compose binds the local API port 8000. The container setup is a development/deployment example, not a hardened production configuration.

## Structure and testing

- `agents/`: primary rule workers, FastAPI, mock responder, ledger, and experimental utility modules.
- `derma_vision_ai/`: alternative legacy numeric-rule engine and CLI.
- `enrichment.py`: named domain-enrichment *placeholders*; no imaging or trained inference is implemented.
- `web/`: standalone JavaScript browser demonstration and Node tests.
- `tests/`: Python unit and regression tests.
- `.github/workflows/`: automated Python/JavaScript checks and static-site publishing.

Run `python -m pytest -q` and `node --test web/app.test.mjs` before releasing. The standalone page targets current evergreen desktop and mobile browsers with ES-module support; the Python API is a separate server-based workflow.

## License

[MIT](LICENSE).
