# Robomastr — Project Context Snapshot

**Generated:** 2026-07-14
**Project:** AI Agent control system for the DJI RoboMaster S1 with web dashboard
**Repo:** https://github.com/dominikbachinger124/robomastr.git

---

## 1. Project Overview

- **Purpose:** Web-based AI-agent control dashboard for a DJI RoboMaster S1 robot.
- **Current state:** Target monorepo architecture is mostly implemented.
  - `robot-bridge/` — fully scaffolded FastAPI service with tests.
  - `backend/` — FastAPI app scaffolded with models, services, API, safety layer, and tests.
  - `frontend/` — React 19 + Vite + Tailwind v4 dashboard scaffolded.
  - Legacy standalone scripts remain at repo root for direct SDK testing.

---

## 2. Architecture

```
robomastr/
├── backend/              # Python 3.12+ — FastAPI + Pydantic v2
│   ├── app/
│   │   ├── api/          # REST routers + WebSocket + video proxy
│   │   ├── models/       # Pydantic v2 models (robot, gamepad, recording)
│   │   ├── services/     # Business logic + robot bridge HTTP client
│   │   └── core/         # Config, structured logging, safety limits
│   └── tests/
├── robot-bridge/         # Python 3.8 ONLY — isolated robomaster SDK service
│   ├── app/
│   │   ├── main.py       # FastAPI server
│   │   ├── robot.py      # Direct robomaster SDK wrapper
│   │   ├── video.py      # MJPEG capture/streaming
│   │   ├── config.py     # Settings
│   │   └── logging.py    # Structured JSON logger
│   └── tests/
├── frontend/             # React 19 + Vite + Tailwind CSS v4 + shadcn/ui
│   └── src/
│       ├── pages/Dashboard.tsx
│       ├── components/   # ConnectionPanel, DiagnosticsPanel, GamepadPanel, RobotStatus, VideoFeed
│       ├── hooks/        # useGamepad, useWebSocket
│       ├── types/        # TypeScript interfaces mirroring backend models
│       └── lib/api.ts    # API client
├── commands/             # Agent command prompts (prime.md, execute.md, etc.)
├── docs/                 # PROJECT_CONTEXT.md, fehler.md
├── reference/            # SDK and control guides
├── plans/                # 01–04 implementation plans
└── *.py (legacy scripts) # test_robot.py, test_gimbal.py, video.py, etc.
```

### Backend layers
- `models/` → `services/` → `api/`
- Business logic never lives in API handlers.
- Main backend never imports `robomaster`; it calls `robot-bridge` via HTTP.

### Robot bridge endpoints
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health`, `/ready` | Health/readiness |
| POST | `/connect` | Connect to robot (`ap`, `sta`, `rndis`) |
| POST | `/disconnect` | Disconnect from robot |
| POST | `/chassis/move` | Move chassis (`x`, `y`, `z` speeds) |
| POST | `/chassis/stop` | Stop chassis |
| POST | `/gimbal/move` | Move gimbal (`pitch_speed`, `yaw_speed`) |
| POST | `/gimbal/stop` | Stop gimbal |
| POST | `/blaster/fire` | Fire blaster once |
| POST | `/led/test` | Run diagnostic LED sequence (~6.5 s) |
| GET | `/status` | Robot telemetry |
| GET | `/video/stream` | MJPEG live stream |

### Backend endpoints
| Method | Path | Purpose |
|--------|------|---------|
| WS | `/api/robot/control` | Real-time control + telemetry |
| POST | `/api/robot/connect` | Proxy connect to bridge |
| POST | `/api/robot/disconnect` | Proxy disconnect |
| GET | `/api/robot/status` | Proxy status (connection test) |
| POST | `/api/robot/test-led` | Proxy LED test command |
| GET | `/api/video/stream` | Proxy MJPEG stream |
| POST | `/api/recording/start` | Start recording stub |
| POST | `/api/recording/stop` | Stop recording stub |
| GET | `/api/recording/status` | Recording status |

---

## 3. Tech Stack

| Layer | Technologies |
|-------|-------------|
| Backend language | Python 3.12+ |
| Backend framework | FastAPI + Pydantic v2 |
| Agent framework | Pydantic AI v2 (planned) |
| Observability | Structured JSON logging wrapper (Logfire target) |
| Robot SDK | `robomaster` (Python 3.8 only) |
| Robot bridge language | Python 3.8 |
| Frontend language | TypeScript strict |
| Frontend framework | React 19 + Vite |
| Styling | Tailwind CSS v4 |
| UI components | shadcn/ui (`@/components/ui/` read-only) |
| Package managers | `uv` (Python), `pnpm` (frontend) |
| Python lint/format | `ruff` |
| Python type check | `mypy --strict` |
| Python tests | `pytest` + `pytest-asyncio` |
| Frontend lint | ESLint |
| Frontend type check | TypeScript `strict: true` (`tsc -b`) |

---

## 4. Core Principles & Conventions

1. **Safety first:** All robot commands pass through safety validation.
   - Max AI linear speed: **0.5 m/s**
   - Max angular speed: **180 °/s**
   - Max gimbal speed: **90 °/s**
   - Dead zone, rate limiter, and dead man's switch on gamepad control.
2. **Type safety everywhere:** `mypy --strict` and TS `strict: true`. No `Any` without justification.
3. **Never import `robomaster` in main backend.** Always delegate to `robot-bridge/` via HTTP.
4. **Structured logging:** JSON formatter, keyword args become fields. No `print()` in production.
5. **Backend models ↔ Frontend types must match exactly.** Update both sides when contracts change.
6. **Agent tool docstrings:** Write for LLM comprehension with `Use this when`, `Do NOT use for`, examples.
7. **Handle all three UI states:** `loading`, `empty`, `success`.
8. **Three-layer backend:** `models/` → `services/` → `api/`.
9. **Tests:** Mock robot SDK; never require physical hardware.

---

## 5. Key Configuration

### Backend defaults (`backend/app/core/config.py`)
- `app_name`: RoboMastr Backend
- `host`: 0.0.0.0, `port`: 8006
- `robot_bridge_url`: `http://localhost:8005`
- `frontend_origin`: `http://localhost:5173`
- `commands_per_second`: 60
- `dead_mans_switch_ms`: 500
- `recordings_dir`: `../recordings`

### Robot bridge defaults (`robot-bridge/app/config.py`)
- `app_name`: RoboMastr Robot Bridge
- `host`: 0.0.0.0, `port`: 8005
- `default_conn_type`: `ap`
- `max_linear_speed_mps`: 0.5
- `max_angular_speed_dps`: 180.0
- `max_gimbal_speed_dps`: 90.0

### Port Scheme
- Backend: `http://localhost:8006`
- Robot bridge: `http://localhost:8005`
- Frontend dev server: `http://localhost:5173`
- Vite proxies `/api` to `http://localhost:8006` and WebSocket to `ws://localhost:8006`.
- Ports 8000 and 8001 are already in use by other processes and are not used by this project.

---

## 6. Development Commands

### Backend
```bash
cd backend/
uv sync
uv run uvicorn app.main:app --reload --port 8006
uv run pytest
uv run ruff check . && uv run ruff format .
uv run mypy app/
```

### Robot bridge (Python 3.8)
```bash
cd robot-bridge/
uv sync
uv run uvicorn app.main:app --reload --port 8005
uv run pytest
uv run ruff check . && uv run ruff format .
uv run mypy app/
```

### Frontend
```bash
cd frontend/
pnpm install
pnpm dev
pnpm build
pnpm lint
```

---

## 7. Current State (Git)

- **Branch:** `main`
- **Status:** ahead of `origin/main` by 4 commits
- **Modified:**
  - `robot-bridge/app/main.py` — added Python 3.8 compatible `_to_thread` helper and `/led/test` endpoint.
  - `robot-bridge/app/robot.py` — added `run_led_test()` diagnostic method.
  - `robot-bridge/tests/conftest.py` — added `led` mock and `mock_led_module` fixture.
  - `robot-bridge/tests/test_api.py` — added LED endpoint tests.
  - `robot-bridge/tests/test_robot_controller.py` — added `test_run_led_test`.
  - `backend/app/services/robot_bridge_client.py` — added `test_led()` client method.
  - `backend/app/api/robot.py` — added `/api/robot/test-led` endpoint.
  - `backend/tests/conftest.py` — added `test_led` to mock bridge client.
  - `backend/tests/test_robot_api.py` — new backend API tests.
  - `frontend/src/lib/api.ts` — added `getRobotStatus()` and `testLed()` helpers.
  - `frontend/src/components/DiagnosticsPanel.tsx` — new diagnostics UI.
  - `frontend/src/pages/Dashboard.tsx` — integrated `DiagnosticsPanel`.
  - `info.md` — this file.
- **Untracked directories/files:**
  - `backend/`
  - `frontend/`
  - `plans/01-robot-bridge.md`
  - `plans/02-backend-api.md`
  - `plans/03-frontend-ui.md`
  - `plans/04-integration-and-recording.md`
  - `robot-bridge/test_sdk_connect.py`
  - `robot-bridge/uv.lock`

### Recent commits
- `ea6266c` feat(robot-bridge): add isolated DJI RoboMaster SDK bridge with HTTP API and tests
- `4e80869` docs: add archon error log
- `c2b91ed` add archon project context
- `755a251` before archon setup
- `07eb6b1` chore: clean up examples and add SDK reference guide

---

## 8. Tests

### Backend tests (`backend/tests/`)
- `test_robot_api.py` — REST endpoint tests including `/api/robot/test-led`
- `test_robot_control.py`
- `test_safety.py`
- `test_video.py`
- `test_websocket.py`

### Robot bridge tests (`robot-bridge/tests/`)
- `test_api.py` — includes `/led/test` tests
- `test_robot_controller.py` — includes `run_led_test` test
- `test_video_streamer.py`

### Frontend tests
- None yet (`frontend/tests/` does not exist).

---

## 9. Important Observations

1. `README.md` is **stale** — it claims no `backend/`, `frontend/`, or `robot-bridge/` exists and describes legacy scripts as the active code. Update it.
2. Ports 8000 and 8001 are already in use by other processes; the project uses 8006 (backend) and 8005 (robot bridge).
3. Backend `RobotState` fields (`current_speed_mps`, `gimbal_yaw_deg`, `gimbal_pitch_deg`) are filled with defaults because the bridge `/status` currently only returns `connected`, `battery_percent`, and `wifi_signal_dbm`.
4. Recording endpoints are Phase 2 stubs; actual frame/event persistence is Phase 4.
5. `robot-bridge/pyproject.toml` duplicates dev dependencies in both `[project.optional-dependencies] dev` and `[dependency-groups] dev`.
6. Frontend uses absolute imports via `@/` with Vite `resolve.alias`.
7. shadcn/ui primitives in `frontend/src/components/ui/` are read-only; create wrappers in `frontend/src/components/`.
8. **Fixed:** `robot-bridge` previously used `asyncio.to_thread`, which does not exist in Python 3.8. Added a compatibility backport (`_to_thread`) so the bridge now runs and tests pass on Python 3.8.
9. **Added:** Web dashboard now has a **Diagnostics** panel with two buttons:
   - **Test Connection** — fetches `/api/robot/status` to verify the full chain.
   - **Test LEDs** — runs the same sequence as `test_led.py` through `/api/robot/test-led`.
  10. The LED test sequence takes ~6.5 seconds and is run synchronously in a worker thread. The frontend shows a loading state and the result or error when finished.
  11. **Fixed:** WebSocket broadcast no longer crashes when the bridge returns `battery_percent=-1` (the `-1` sentinel is normalized to `0` before creating `RobotState`).
  12. **Wired:** Dashboard robot state is now shared across REST actions. `ConnectionPanel` and `DiagnosticsPanel` report the resulting `RobotState` to `Dashboard` via `onRobotStateUpdate`, so the `RobotStatus` badge updates immediately after connect, disconnect, connection tests, and LED tests. The per-second WebSocket broadcast continues to refresh telemetry in the background.
  13. **Verified end-to-end:** The web dashboard is operational with the real robot. Connect/disconnect, telemetry, diagnostics (Test Connection + Test LEDs), and gamepad steering all work.
  14. **Video feed fix:** The MJPEG stream works stand-alone at `http://localhost:8005/video/stream` but failed inside the dashboard (no picture, then system freeze). The fix embeds that exact endpoint in an `<iframe>` in `frontend/src/components/VideoFeed.tsx` so the browser renders the stream independently. This avoids CORS, backend proxy buffering, and browser-specific `<img>` MJPEG decoder issues. Supporting changes:
      - Lowered default capture settings in `robot-bridge/app/config.py` to `360p`, `15 FPS`, JPEG quality `65`.
      - Added CORS middleware to `robot-bridge/app/main.py` for direct bridge access.
      - `frontend/src/lib/api.ts` keeps both `getBridgeVideoStreamUrl()` and `getBackendVideoStreamUrl()` helpers.
      - Backend proxy endpoint `/api/video/stream` remains available as a fallback.
  15. **Pending (low priority):** Allow the user to stop the active MJPEG stream inside the dashboard without pausing the whole `VideoFeed` card. Tracked in todo list.

---

## 10. Safety Limits Reference

```python
MAX_LINEAR_SPEED_MPS = 0.5      # m/s
MAX_ANGULAR_SPEED_DPS = 180.0   # °/s
MAX_GIMBAL_SPEED_DPS = 90.0     # °/s
COMMANDS_PER_SECOND = 60
INPUT_DEAD_ZONE = 0.15
```

These are enforced in both `backend/app/core/safety.py` and `robot-bridge/app/config.py` (clamping in `robot.py`).

---

*This file is a single-source context snapshot. Keep it updated as the project evolves.*
