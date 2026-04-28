# Run the Code - Task Plan

## Information Gathered
- This is a full-stack AI Document Intelligence Platform
- **Backend**: FastAPI (Python), uses SQLite by default, `venv` exists, dependencies installed
- **Frontend**: React + Vite, `node_modules` exists, configured to call `http://127.0.0.1:8000`
- Database (`document_intelligence.db`) already exists with data

## Plan
1. Start the backend FastAPI server on `http://127.0.0.1:8000`
2. Start the frontend Vite dev server
3. Verify both services are healthy

## Commands to Execute
- Backend: `cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- Frontend: `cd frontend && npm run dev`

## Follow-up Steps
- Verify backend health at `http://127.0.0.1:8000/health`
- Open frontend URL in browser

