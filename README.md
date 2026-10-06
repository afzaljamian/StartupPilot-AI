# StartupPilot AI 🚀

**Multi-Agent AI Startup Co-Pilot** — a B.Tech minor project that converts a plain-English startup idea into a structured business plan using specialized AI agents.

## Why this is not a chatbot

StartupPilot uses a dependency-aware multi-agent pipeline:

**Startup idea → Marketing → Finance → Product → Validator → MongoDB → Dashboard/PDF**

Finance cannot start until Marketing completes; Product depends on Marketing + Finance; Validator audits all three. In live mode, CrewAI creates the specialist agents/tasks and sequential context handoffs. In demo mode, deterministic sample outputs make the complete workflow demonstrable without external API keys.

## Features

- React + Tailwind SaaS dashboard
- FastAPI backend with OpenAPI `/docs` and `/redoc`
- JWT authentication + bcrypt password hashing
- MongoDB Atlas persistence
- Celery + Redis background execution
- CrewAI sequential multi-agent orchestration
- Gemini integration with structured JSON outputs
- Tavily research integration
- Deterministic Python financial calculations
- FastAPI WebSocket progress events via Redis pub/sub
- ReportLab PDF business plan export
- Demo mode for college presentation
- History and previous analyses
- Docker Compose deployment
- Unit tests for core calculations/auth

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, Tailwind CSS, Axios, React Router, Recharts |
| Backend | Python, FastAPI, Pydantic |
| AI | CrewAI, Gemini API |
| Research | Tavily API |
| Queue | Celery + Redis |
| Database | MongoDB Atlas / Motor |
| Auth | JWT + bcrypt |
| PDF | ReportLab |
| Deployment | Docker / Docker Compose |

## Architecture

See [`docs/architecture.md`](docs/architecture.md).

## 1. Environment setup

Copy `.env.example` to `.env` and set a strong JWT secret. For the first demo, leave `DEMO_MODE=true`; MongoDB and Redis are still required.

For live AI, add `GEMINI_API_KEY` and optionally `TAVILY_API_KEY`, then set `DEMO_MODE=false`.

Google's current Gemini documentation recommends the official `google-genai` Python SDK. urlGemini API documentationhttps://ai.google.dev/gemini-api/docs/get-started

## 2. Docker

```bash
cp .env.example .env
docker compose up --build
```

Open:

- Frontend: http://localhost:5173
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

MongoDB is intentionally external so the same setup can point to MongoDB Atlas. The Docker Compose stack provides frontend, backend, worker and Redis.

## 3. Local development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

In another terminal:

```bash
cd backend
celery -A app.tasks.celery_app.celery_app worker --loglevel=INFO
```

Redis must be running and `MONGODB_URI` must point to a MongoDB instance/Atlas cluster.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Optional `.env` in `frontend/`:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## 4. Demo mode

Demo mode is designed for a faculty/viva demonstration. It is clearly labeled in the report as **Demo Mode — simulated AI responses** and never pretends that mock data is live research.

Sample startup idea:

> AI-powered platform that helps college students find affordable healthy meals near their campus.

## 5. Live AI mode

Set:

```env
GEMINI_API_KEY=your_key
TAVILY_API_KEY=your_key
DEMO_MODE=false
```

The Marketing and Finance stages use Tavily research when available. Research sources are preserved for the report. Unsupported statistics are flagged rather than fabricated.

## 6. API endpoints

### Auth

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

### Startup runs

- `POST /api/run`
- `GET /api/run/{run_id}`
- `GET /api/runs`
- `DELETE /api/run/{run_id}`

### Reports

- `GET /api/report/{run_id}`
- `GET /api/report/{run_id}/pdf`

### Health

- `GET /api/health`

### WebSocket

- `WS /ws/{run_id}?token=<JWT>`

## 7. Database schema

### users

`name`, `email`, `password_hash`, `created_at`

### runs

`user_id`, `startup_idea`, optional context fields, `status`, `created_at`, `completed_at`, `error`

### reports

`run_id`, `marketing`, `finance`, `product`, `validation`, `sources`, `generated_at`, `demo_mode`

## 8. Testing

From repository root:

```bash
pytest -q
```

Tests do not require Gemini/Tavily credentials and focus on deterministic calculations and password/JWT primitives. External integrations should be mocked for expanded integration tests.

## 9. Security

- API keys are backend-only.
- `.env` is ignored by Git.
- Passwords are bcrypt hashes.
- Protected REST endpoints require JWT.
- WebSocket connections require a JWT query token.
- Input is validated with Pydantic.
- Internal exceptions are not exposed to clients.
- Agent chain-of-thought is never sent to the frontend.

## 10. PDF export

ReportLab generates a readable business plan containing a cover, executive summary, marketing strategy, financial plan, product requirements, validation report, sources and assumptions/disclaimers.

## 11. Deployment

For Render-compatible deployment, deploy the frontend as a static/site service, the FastAPI backend as a web service, and the Celery worker as a background worker. Use managed Redis and MongoDB Atlas. Set all environment variables in the platform dashboard rather than committing secrets.

## 12. Troubleshooting

**Worker unavailable:** verify Redis URL and that the Celery worker is running.

**MongoDB errors:** verify `MONGODB_URI`, network access and Atlas database user permissions.

**Live AI unavailable:** verify Gemini key/model configuration; use demo mode for presentation.

**No research sources:** verify Tavily key/network access. The system will not fabricate sources.

**WebSocket does not update:** verify Redis is reachable by both backend and worker; the run status remains available through polling.

## 13. Future scope

Legal Compliance Agent, HR Agent, Sales Agent, Competitor Monitoring Agent, Voice Input, Mobile App, Payment Integration, Financial Data APIs, Investor Matching, Pitch Deck Generator, automated plan updates and Market Monitoring Agent.

## Academic contribution

> Using specialized autonomous AI agents that collaborate through context passing to generate a coherent, cross-domain startup plan.

This directly demonstrates AI, agentic AI, multi-agent systems, LLM integration, NLP, APIs, full-stack development, database management, authentication, asynchronous processing, real-time communication, cloud deployment, software architecture, testing and containerization.
