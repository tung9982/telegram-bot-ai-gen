# AetherFlow Studio

Production-grade desktop AI workflow platform using Electron + React Flow + FastAPI.

## Architecture
- **Desktop Shell (Electron):** app lifecycle, multi-window, notifications, packaging.
- **Frontend (React/TypeScript):** cinematic node editor, Zustand state, websocket runtime updates.
- **Backend (FastAPI):** workflow execution API, websocket broadcasting, node registry.
- **Execution Engine:** directed-acyclic-graph orchestration, node dependency resolution, async execution.
- **Extensibility:** plugin folders (`plugins/`) and reusable schemas (`shared/`).

## Folder Structure
- `frontend/` React + Tailwind + React Flow UI.
- `backend/` FastAPI, execution engine, node system.
- `electron/` desktop entrypoint.
- `workflows/` importable workflow templates.
- `shared/` cross-runtime contracts.
- `plugins/` runtime plugin packages.
- `scripts/` automation scripts.
- `assets/` visual/media assets.

## Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Electron Setup
```bash
npm install --save-dev electron electron-builder
VITE_DEV_SERVER_URL=http://localhost:5173 electron electron/main.js
```

## Deployment
- Build frontend with `npm run build`.
- Containerize backend using your existing Docker + uvicorn process manager.
- Package desktop app with `electron-builder --win` for Windows executable output.

## Example Pipeline
See `workflows/example_storyboard_pipeline.json` for:
Prompt → Prompt Enhancer → Storyboard → Image Gen → Image-to-Video → Voice → Subtitles → FFmpeg Export.
