# Robomastr — Project Context

> Auto-generated project overview for AI agents and new contributors.
> Last updated: 2026-07-13

---

## 1. What Is This?

AI Agent control system for the **DJI RoboMaster S1** robot with a web dashboard.
- Backend: Python 3.12+ (FastAPI + Pydantic AI)
- Frontend: React 19 + Vite + Tailwind CSS v4 + shadcn/ui
- Robot bridge: Isolated Python 3.8 service (robomaster SDK)
- Max AI-controlled robot speed: **0.5 m/s** (hard safety limit)

---

## 2. Architecture Overview

```
robomastr/
├── backend/              # Python 3.12+ — Main API, AI agents, business logic
│   ├── app/
│   │   ├── api/          # FastAPI routers (thin HTTP layer)
│   │   ├── models/       # Pydantic v2 models (validation + schemas)
│   │   ├── services/     # Business logic + robot bridge HTTP client
│   │   ├── core/         # Config, logging, safety limits
│   │   └── agents/       # Pydantic AI agent definitions + tools
│   ├── tests/
│   ├── pyproject.toml
│   └── uv.lock
├── robot-bridge/         # Python 3.8 ONLY — isolated robomaster SDK service
│   ├── app/
│   │   ├── main.py       # Lightweight FastAPI/Flask server
│   │   └── robot.py      # Direct robomaster SDK calls
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/             # React 19 + Vite + Tailwind v4
│   ├── src/
│   │   ├── components/   # React components
│   │   │   └── ui/       # shadcn/ui primitives (read-only)
│   │   ├── types/        # TypeScript interfaces (mirror backend models)
│   │   ├── hooks/        # Custom React hooks
│   │   └── lib/          # Utilities, API client
│   ├── tests/
│   ├── package.json
│   └── pnpm-lock.yaml
└── .github/workflows/    # CI pipelines (lint, typecheck, test)
```

**Three-layer backend**: `models/` → `services/` → `api/`. Never put business logic in API handlers.

---

## 3. Tech Stack

| Layer | Tech |
|-------|------|
| Backend Lang | Python 3.12+ (main), Python 3.8 (robot bridge only) |
| Backend Framework | FastAPI + Pydantic v2 |
| Agent Framework | Pydantic AI v2 (`pydantic-ai`) |
| Observability | Pydantic Logfire (OpenTelemetry) — no `print()` in production |
| Robot SDK | `robomaster` (pip) — requires Python 3.8 |
| Package Manager | `uv` (Python), `pnpm` (frontend) |
| Lint/Format | `ruff` (Python), ESLint + Prettier (TS) |
| Type Check | `mypy --strict` (Python), TypeScript `strict: true` |
| Test | `pytest` + `pytest-asyncio` (Python), `pnpm test` (frontend) |
| Frontend Lang | TypeScript (strict) |
| Frontend Framework | React 19 + Vite |
| Styling | Tailwind CSS v4 |
| UI Components | shadcn/ui (`@/components/ui/`) |
| State | React hooks + Context (keep simple) |

---

## 4. Quick Start

### Backend
```bash
# Install dependencies
uv sync

# Run dev server with auto-reload
uv run uvicorn app.main:app --reload --port 8000

# Run tests
uv run pytest

# Lint and format
uv run ruff check . && uv run ruff format .

# Type check
uv run mypy app/
```

### Frontend
```bash
# Install dependencies
pnpm install

# Run dev server
pnpm dev

# Build for production
pnpm build

# Run tests
pnpm test

# Lint and format
pnpm lint && pnpm format
```

### Robot Bridge (Python 3.8)
```bash
cd robot-bridge/
pip install -r requirements.txt
python app/main.py  # or via Docker
```

---

## 5. Key Files & Conventions

| File | Purpose |
|------|---------|
| `CLAUDE.md` | **Read this first** — coding rules, architecture, conventions |
| `backend/app/core/` | Config, logging, safety limits |
| `backend/app/models/` | Pydantic models with `Field(..., description=..., ge=..., le=...)` |
| `backend/app/services/` | Business logic — pure functions/classes with type hints |
| `backend/app/api/` | FastAPI `APIRouter` with `prefix`, `tags`, `response_model` |
| `backend/app/agents/` | Pydantic AI `Agent` with tools, safety validation before SDK calls |
| `frontend/src/types/` | TypeScript interfaces that **must mirror** backend Pydantic models |
| `frontend/src/components/ui/` | shadcn/ui primitives — **read-only**, do not modify |

---

## 6. Critical Rules

1. **Safety First**: All robot commands pass through safety validation. Max AI speed = 0.5 m/s. No exceptions.
2. **Never import `robomaster` in main backend**. Always delegate to `robot-bridge/` via HTTP.
3. **Type safety everywhere**: `strict: true` (TypeScript) and `mypy --strict` (Python). No `Any` without justification.
4. **Structured logging**: Use Pydantic Logfire. No `print()` in production code.
5. **Backend models ↔ Frontend types must match exactly**. Update both sides when contracts change.
6. **Handle all three UI states**: `loading`, `empty`, and `success` in every frontend component.
7. **Agent tool docstrings**: Write for LLM comprehension — include `Use this when`, `Do NOT use for`, and examples.

---

## 7. API Contracts (Backend ↔ Frontend)

| Python | TypeScript |
|--------|-----------|
| `int` | `number` |
| `float` | `number` |
| `Decimal` | `string` |
| `datetime` | `string` (ISO 8601) |
| `bool` | `boolean` |
| `str` | `string` |

Error handling: Backend returns `{"detail": "..."}` for 4xx/5xx. Frontend intercepts and displays user-friendly messages.

---

## 8. Testing Strategy

- **Backend**: Mock robot SDK in unit tests. Use `TestClient` for API integration tests.
- **Frontend**: React Testing Library for component tests.
- **Agent tools**: Verify safety validation rejects unsafe params.
- Never require physical hardware to run the test suite.

---

## 9. Risks & Constraints

| Risk | Impact | Mitigation |
|------|--------|------------|
| Robot SDK requires Python 3.8 | HIGH | Strict isolation via `robot-bridge/` service + Docker |
| Physical robot damage from unsafe commands | HIGH | Safety validation layer, max 0.5 m/s AI speed |
| Type drift between backend/frontend | MED | Mirror types in `frontend/src/types/` exactly |
| Logfire not configured → silent failures | LOW | Never use `print()`, always use structured logging |
| shadcn/ui components modified | LOW | `components/ui/` is read-only; create wrappers in `components/` |

---

## 10. Git & CI

- Monorepo with `backend/` and `frontend/` at repository root.
- GitHub Actions: lint, typecheck, test on push/PR.
- LLM: OpenAI by default; Ollama/local models configurable via env.

---

*For full details see `CLAUDE.md` in the repository root.*
