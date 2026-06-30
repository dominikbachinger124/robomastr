# Robomastr – AI Agent Global Rules

Project: DJI RoboMaster S1 AI Agent with Web Dashboard
Repo: https://github.com/dominikbachinger124/robomastr.git

---

## 1. Core Principles

- **Safety First**: All robot commands pass through a safety validation layer. Max AI speed = 0.5 m/s. No exceptions.
- **Type Safety Everywhere**: Strict TypeScript (`strict: true`) and mypy (`strict = true`). No `Any` without justification.
- **Agent-Optimized Tooling**: Pydantic AI tool docstrings guide LLM tool selection. Write for agent comprehension, not just human readers.
- **Structured Logging**: Use Pydantic Logfire (OpenTelemetry) for all observability. No `print()` in production code.
- **Three-Layer Backend**: `models/` → `services/` → `api/`. HTTP handlers are thin; business logic lives in services.
- **Convention over Configuration**: Follow existing patterns in `reference/` and `commands/`. When in doubt, ask.

---

## 2. Tech Stack

### Backend
- **Language**: Python 3.12+ (main backend), Python 3.8 (robot bridge only)
- **Framework**: FastAPI + Pydantic v2
- **Agent Framework**: Pydantic AI v2 (`pydantic-ai`)
- **Observability**: Pydantic Logfire (structured logging + tracing)
- **Robot SDK**: `robomaster` (pip install) — requires Python 3.8
- **Package Manager**: `uv` (modern Python toolchain)
- **Lint/Format**: `ruff` (replaces flake8, black, isort)
- **Type Check**: `mypy --strict`
- **Test**: `pytest` with `pytest-asyncio`

### Frontend
- **Language**: TypeScript (strict)
- **Framework**: React 19 + Vite
- **Styling**: Tailwind CSS v4
- **UI Components**: shadcn/ui (`@/components/ui/`)
- **State Management**: React hooks + Context (keep simple; no Redux unless needed)
- **Package Manager**: `pnpm`
- **Lint/Format**: ESLint + Prettier

### Infrastructure
- **Monorepo**: `backend/` and `frontend/` at repository root
- **CI/CD**: GitHub Actions (lint, typecheck, test on push/PR)
- **LLM**: OpenAI by default; Ollama/local models configurable via env

---

## 3. Architecture

```
robomastr/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI routers (thin HTTP layer)
│   │   ├── models/        # Pydantic models (validation + schemas)
│   │   ├── services/      # Business logic + robot bridge client
│   │   ├── core/          # Config, logging, safety limits
│   │   └── agents/        # Pydantic AI agent definitions + tools
│   ├── tests/
│   ├── pyproject.toml
│   └── uv.lock
├── robot-bridge/          # Python 3.8 ONLY — isolated robomaster SDK service
│   ├── app/
│   │   ├── main.py        # Lightweight FastAPI/Flask server
│   │   └── robot.py       # Direct robomaster SDK calls
│   ├── requirements.txt
│   └── Dockerfile         # python:3.8-slim base
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   │   └── ui/        # shadcn/ui primitives (read-only)
│   │   ├── types/         # TypeScript interfaces (mirror backend models)
│   │   ├── hooks/         # Custom React hooks
│   │   └── lib/           # Utilities, API client
│   ├── tests/
│   ├── package.json
│   └── pnpm-lock.yaml
├── .github/workflows/     # CI pipelines
└── CLAUDE.md              # This file
```

### Backend Patterns
- **Models**: Pydantic v2 `BaseModel` with `Field(..., description=..., ge=..., le=...)`
- **Services**: Pure functions/classes with type hints. Log entry/exit with contextual fields.
- **API**: FastAPI `APIRouter` with `prefix`, `tags`, and `response_model` always specified.
- **Agents**: Pydantic AI `Agent` with `deps_type`, tools registered via `@agent.tool`, safety validation before SDK calls.
- **Robot Bridge**: Main backend NEVER imports `robomaster` directly. Always calls `robot-bridge/` service via HTTP.

### Frontend Patterns
- **Components**: `export function ComponentName({ prop }: Props)` with explicit Props interface
- **UI States**: Always handle `loading`, `empty`, and `success` states explicitly
- **Styling**: Tailwind utilities only. No custom CSS files. Use design system colors (`text-foreground`, `bg-primary`)

---

## 4. Code Style

### Python
- **Functions**: `snake_case`, type hints on all params and returns
- **Classes**: `PascalCase`
- **Variables**: `snake_case`, verbose names (`robot_speed_mps`, not `s`)
- **Constants**: `SCREAMING_SNAKE_CASE` in safety/config modules
- **Docstrings**: Google style with sections: one-line summary, `Use this when`, `Do NOT use for`, `Args`, `Returns`, `Performance Notes`, `Examples`

```python
# Good
class MoveCommand(BaseModel):
    """Validated move command for chassis control."""
    distance_mm: int = Field(..., ge=0, le=5000, description="Distance in millimeters")
    speed: float = Field(..., ge=0.0, le=0.5, description="Speed in m/s (AI safety limit)")

# Bad
class moveCommand(BaseModel):
    distance: int  # missing validation, vague name
```

### TypeScript
- **Components**: `PascalCase` files + function names
- **Props interfaces**: `ComponentNameProps`
- **Variables**: `camelCase`
- **Types**: `PascalCase`, use `interface` for objects, `type` for unions
- **JSDoc**: Every prop gets a JSDoc comment

```typescript
// Good
interface RobotStatusProps {
  /** Whether the robot is currently connected via WiFi */
  isConnected: boolean;
  /** Current battery percentage 0-100 */
  batteryPercent?: number;
}

export function RobotStatus({ isConnected, batteryPercent }: RobotStatusProps) {
  // ...
}
```

---

## 5. Logging

Use Pydantic Logfire for structured, OpenTelemetry-compatible logging.

```python
from pydantic_logfire import Logfire

logfire = Logfire()

# In services
logfire.info("operation_started", operation="move_forward", distance_mm=1000, speed=0.3)

# On errors
logfire.error("robot_connection_failed", error=str(e), ip=robot_ip)
```

**What to log**:
- Service entry/exit with operation name and key parameters
- API requests (endpoint, method, status)
- Robot SDK calls (command, parameters, result)
- Errors with full context (traceback, connection state)

**Never log**: Passwords, API keys, raw image data, or anything >1KB per event.

---

## 6. Testing

### Backend
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=term-missing

# Single test
uv run pytest tests/test_robot_service.py::test_move_forward_safety -v
```

- Test file naming: `test_<module>.py`
- Unit tests for services (mock robot SDK)
- Integration tests for API endpoints (TestClient)
- Agent tool tests: verify safety validation rejects unsafe params

### Frontend
```bash
# Run tests
pnpm test

# Single test
pnpm test RobotStatus
```

- Component tests with React Testing Library
- Test file naming: `<ComponentName>.test.tsx` co-located or in `tests/`

---

## 7. API Contracts

Backend Pydantic models and frontend TypeScript interfaces must match exactly.

```python
# backend/app/models/robot.py
class RobotStatus(BaseModel):
    is_connected: bool
    battery_percent: int = Field(..., ge=0, le=100)
    current_speed_mps: float = Field(..., ge=0.0)
```

```typescript
// frontend/src/types/robot.ts
export interface RobotStatus {
  is_connected: boolean;
  battery_percent: number;  // matches Python int
  current_speed_mps: number; // matches Python float
}
```

**Decoding rules**:
- Python `Decimal` → TypeScript `string` (JSON serialization)
- Python `datetime` → TypeScript `string` (ISO 8601)
- Python `int` → TypeScript `number`
- Python `float` → TypeScript `number`

**Error handling**: Backend returns `{"detail": "..."}` for 4xx/5xx. Frontend intercepts HTTP errors and displays user-friendly messages.

---

## 8. Common Patterns

### Backend: Service + API Layer

```python
# app/services/robot.py
from app.core.logging import get_logger
from app.models.robot import MoveCommand
import httpx

logger = get_logger(__name__)
ROBOT_BRIDGE_URL = "http://localhost:8001"

async def move_chassis(cmd: MoveCommand) -> str:
    """Move chassis via robot bridge with safety logging."""
    logger.info("move_started", distance=cmd.distance_mm, speed=cmd.speed)
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{ROBOT_BRIDGE_URL}/move",
            json={"distance_mm": cmd.distance_mm, "speed": cmd.speed}
        )
        resp.raise_for_status()
    logger.info("move_completed")
    return f"Moved {cmd.distance_mm}mm"

# app/api/robot.py
from fastapi import APIRouter
from app.models.robot import MoveCommand, MoveResponse
from app.services import robot_service

router = APIRouter(prefix="/api/robot", tags=["robot"])

@router.post("/move", response_model=MoveResponse)
async def move(cmd: MoveCommand) -> MoveResponse:
    result = await robot_service.move_chassis(cmd)
    return MoveResponse(status=result)
```

### Frontend: Component with States

```typescript
// src/components/RobotControl.tsx
import { useState } from "react";
import { Button } from "@/components/ui/button";

interface RobotControlProps {
  onMove: (distance: number) => Promise<void>;
}

export function RobotControl({ onMove }: RobotControlProps) {
  const [loading, setLoading] = useState(false);

  if (loading) return <p>Moving...</p>;

  return (
    <div className="flex gap-2">
      <Button onClick={() => { setLoading(true); onMove(1000).finally(() => setLoading(false)); }}>
        Forward 1m
      </Button>
    </div>
  );
}
```

### Agent Tool Pattern

```python
@robot_agent.tool
async def move_forward(
    ctx: RunContext[RobotDependencies],
    distance_mm: int = Field(..., ge=0, le=5000),
    speed: float = Field(..., ge=0.0, le=0.5),
) -> str:
    """Move chassis forward.

    Use this when you need to:
    - Navigate to a target position
    - Move the robot in a straight line forward

    Do NOT use this for:
    - Rotating in place (use rotate_chassis instead)
    - Emergency stops (use emergency_stop instead)

    Args:
        distance_mm: Distance to move in millimeters (0-5000)
        speed: Movement speed 0.0-0.5 m/s (safety limit for AI ops)

    Returns:
        Status message with final position or error
    """
    cmd = MoveCommand(distance_mm=distance_mm, speed=speed)
    is_safe, reason = cmd.validate_safety()
    if not is_safe:
        return f"Move rejected: {reason}"
    try:
        # Delegate to robot-bridge service (Python 3.8)
        result = await ctx.deps.robot_bridge.move(cmd)
        return f"Moved forward {distance_mm}mm at {speed}m/s"
    except Exception as e:
        logger.error("move_failed", error=str(e))
        return f"Move failed: {str(e)}"
```

---

## 9. Development Commands

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

---

## 10. AI Coding Assistant Instructions

1. **Always read CLAUDE.md first** before making changes. These rules override general conventions.
2. **Follow the three-layer pattern**: models → services → api. Never put business logic in API handlers.
3. **Validate robot safety before any SDK call**. Max AI speed is 0.5 m/s. Return descriptive rejections.
4. **Never import `robomaster` in the main backend**. The main backend is Python 3.12+; the SDK requires 3.8. Always delegate to `robot-bridge/` via HTTP.
5. **Write agent tool docstrings for LLM comprehension**: include `Use this when`, `Do NOT use for`, and concrete examples.
6. **Match backend models to frontend types exactly**. Update both sides when contracts change.
7. **Use structured logging (Logfire) for all observability**. No `print()` statements.
8. **Run linters and type checkers before declaring done**: `ruff`, `mypy`, ESLint, TypeScript strict.
9. **Handle all three UI states**: `loading`, `empty`, and `success` in every frontend component.
10. **Mock the robot SDK in backend tests**. Never require physical hardware to run the test suite.
