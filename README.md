# LinkFlow

AI-powered ecosystem relationship automation platform. Automates mentor-company matching, relationship lifecycle management, and coordination workflows for innovation programmes.

## Team ownership

| Person | Area |
|--------|------|
| Person A | Backend: `main.py`, all `routers/` |
| Person B | AI services: `services/pdf_parser.py`, `services/gemini_matcher.py`, `services/workflow_engine.py` |
| Person C | Data layer: `services/firebase_client.py`, `models/`, Firebase project setup |
| Person D | Frontend: all of `frontend/src/` |

## Prerequisites

- Python 3.11+
- Node 18+
- [Ollama](https://ollama.com) installed with llama3 pulled (`ollama pull llama3`)
- Firebase project with Firestore enabled
- Gemini API key from [Google AI Studio](https://aistudio.google.com)

## Setup

1. Clone the repo
2. `cp backend/.env.example backend/.env` and fill in `GEMINI_API_KEY` and `FIREBASE_CREDENTIALS_PATH`
3. Place your Firebase service account JSON at `backend/firebase-credentials.json`
4. Run: `docker-compose up`
5. Open [http://localhost:5173](http://localhost:5173)

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/onboarding/upload` | Upload a PDF to extract and onboard an actor profile |
| GET | `/api/actors` | List all actors (optional `?type=` filter) |
| GET | `/api/actors/{id}` | Get a single actor by ID |
| POST | `/api/match` | Run AI matching against a natural language query |
| POST | `/api/match/approve` | Approve a match and create a relationship |
| GET | `/api/relationships` | List relationships (optional `actor_id`, `state`, `programme_id` filters) |
| GET | `/api/relationships/{id}` | Get a single relationship |
| POST | `/api/relationships/{id}/session` | Log a session against a relationship |
| PATCH | `/api/relationships/{id}/state` | Update relationship state |
| GET | `/api/workflows/stale` | Find stale relationships and generate nudge messages |
| GET | `/api/workflows/events` | Fetch last 50 workflow events |

## Running without Docker

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Architecture note

PDF parsing uses **Ollama (local Llama 3)** — data never leaves the machine. Chat matching uses **Gemini API** — only anonymised profile summaries are sent, no raw documents.
