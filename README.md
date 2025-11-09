# Quantum Circuit Playground

An interactive two-qubit circuit simulator with a React + TypeScript frontend and a FastAPI backend. The interface mirrors the reference sketch (see `/mnt/data/WhatsApp Image 2025-11-09 at 10.27.29.jpeg`) featuring gate toggles, LEDs, measurements, and trial runs to explore superposition and entanglement.

## Features
- Landscape-first responsive UI with rotate hint for portrait devices.
- Gate toggles for X (G1), H (G2), and CNOT (G3) with aura animation and LED blink feedback.
- Secure measurement logic (single-qubit or both) with proper collapse and renormalization.
- Trial runner to demonstrate probabilistic outcomes and Bell state correlations.
- SQLite persistence for sessions, gate actions, and trial history.
- Containerized deployment (Docker Compose + Kubernetes manifests) and GitHub Actions CI.

## Technology Stack
- **Frontend:** React 18, TypeScript, Vite, TailwindCSS, Framer Motion, Axios, WebSocket-ready API client.
- **Backend:** FastAPI, Python 3.11, NumPy, Pydantic.
- **Database:** SQLite stored under `api/data/quantum.db`.
- **Tooling:** Docker, docker compose, Kubernetes manifests, GitHub Actions, pytest.

## Prerequisites
- Node.js 20+
- Python 3.11+
- Docker & docker compose plugin
- (Optional) kubectl and a Kubernetes cluster for manifests

## Quick Start (Recommended)
1. Ensure the script is executable:
   ```bash
   chmod +x scripts/apply.sh
   ```
2. Run the apply script from the repository root:
   ```bash
   ./scripts/apply.sh
   ```
   The script ensures the folder tree exists, installs frontend/backend dependencies, builds the frontend, builds Docker images, and launches the stack via docker compose.
3. Visit the running services:
   - Frontend: http://localhost:5173
   - API health: http://localhost:8000/api/health

### Manual end-to-end checklist
Follow this checklist if you prefer to step through each stage yourself or need to troubleshoot a specific layer of the stack:

1. **Backend deps:**
   ```bash
   cd api
   python3 -m pip install --upgrade pip
   python3 -m pip install -r requirements.txt
   ```
2. **Backend smoke test:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
   Browse to `http://localhost:8000/api/health` to confirm a `{"status": "ok"}` response, then stop the server (Ctrl+C).
3. **Frontend deps and dev server:**
   ```bash
   cd ../frontend
   npm install
   npm run dev -- --host 0.0.0.0 --port 5173
   ```
   Visit `http://localhost:5173` to interact with the UI. Stop the dev server when finished.
4. **Automated checks:**
   ```bash
   cd ../api
   pytest
   cd ../frontend
   npm run typecheck
   ```
5. **Container workflow:**
   ```bash
   cd ..
   docker compose -f deploy/docker-compose.yml build
   docker compose -f deploy/docker-compose.yml up -d
   ```
   Tail the logs with `docker compose -f deploy/docker-compose.yml logs -f` and shut everything down with `docker compose -f deploy/docker-compose.yml down` when you are done.

## Manual Setup
### Backend
```bash
cd api
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

> **Note:** Some environments may block access to scoped npm packages (e.g., `@types/*`). If you encounter HTTP 403 errors, configure your npm registry mirror accordingly before running `npm install`.

## Docker Compose Workflow
```bash
docker compose -f deploy/docker-compose.yml build
docker compose -f deploy/docker-compose.yml up -d
docker compose -f deploy/docker-compose.yml logs -f
```
Volumes:
- `../api/data:/app/data` persists the SQLite file outside the container.

Stop the stack with:
```bash
docker compose -f deploy/docker-compose.yml down
```

## Kubernetes Deployment
Apply manifests in the following order:
```bash
kubectl apply -f deploy/k8s/namespace.yaml
kubectl apply -f deploy/k8s/api-pvc.yaml
kubectl apply -f deploy/k8s/api-deploy.yaml
kubectl apply -f deploy/k8s/api-service.yaml
kubectl apply -f deploy/k8s/frontend-deploy.yaml
kubectl apply -f deploy/k8s/frontend-service.yaml
kubectl apply -f deploy/k8s/ingress.yaml
```
The PVC requests `ReadWriteMany`; ensure your StorageClass supports multi-writer access or switch to a managed database for production workloads.

## Development Utilities
- `scripts/dev.sh up|down|logs|test` for quick docker compose management and running backend tests.
- GitHub Actions (`.github/workflows/ci.yml`) runs `npm ci`, `npm run typecheck`, and `pytest` on every push/PR targeting `main`.

## Testing
Backend unit tests:
```bash
cd api
pytest
```

The tests cover gate math (Hadamard balance, Bell state outcomes), measurement normalization, and API lifecycle checks.

## UI Guide
1. **Gate Toggles:** Click G1 (X) or G2 (H) on Q1 to apply the corresponding gate. G3 (CNOT) entangles Q1 → Q2. Active gates emit a soft aura for ~1.2 s.
2. **LEDs:** Located to the right of each qubit line. Green represents `|0⟩`, red represents `|1⟩`. LEDs blink for 600 ms when a measurement or reset changes the value.
3. **Measurements:** Use the Measure buttons on each qubit or the combined “Measure BOTH” button below the CNOT tile. Buttons are momentary; measurements collapse the state according to the backend physics model.
4. **Resets:** Reset individual qubits or use Hard Reset to clear toggles and restore `|00⟩`.
5. **Trials:** Choose scope (Q1/Q2/BOTH), set the number of runs, and click “Run Trials” to sample repeated measurements. After applying H then CNOT, the Bell pair produces only `00` and `11` outcomes near 50/50.

## Troubleshooting
- **NPM 403 errors:** Configure the npm registry mirror (`npm config set registry https://registry.npmjs.org/`) or use corporate credentials if required.
- **Docker permission issues:** Ensure your user has permission to run Docker, or execute commands with `sudo` if necessary.
- **Kubernetes storage errors:** Switch the PVC to an appropriate access mode or back the API with a cloud database for multi-writer deployments.

Enjoy exploring quantum logic with visual feedback and persistent sessions!
