# Robomastr

AI Agent control system for the DJI RoboMaster S1 with a web dashboard.

> **Project rules and conventions:** See [`CLAUDE.md`](./CLAUDE.md) in the repository root.  
> **Project context snapshot:** See [`docs/PROJECT_CONTEXT.md`](./docs/PROJECT_CONTEXT.md).

---

## Project Status

This repository is currently in an early/experimental phase. The target architecture
(FastAPI backend + React frontend + isolated robot bridge) is documented in
`CLAUDE.md`, but the active code consists of standalone Python scripts that exercise
the official DJI `robomaster` SDK directly.

There is no `package.json`, `pyproject.toml`, `backend/`, `frontend/`, or `robot-bridge/`
folder yet. Use the commands below to work with the code that exists today.

---

## Prerequisites

- **Python 3.8 – 3.9** for the official DJI [`robomaster`](https://pypi.org/project/robomaster/)
  SDK (the SDK is **not** compatible with Python 3.10+).
- A **DJI RoboMaster S1** or **EP** reachable via USB/RNDIS, direct Wi-Fi (AP mode),
  or router (STA mode).
- Optional, depending on script: `opencv-python` for camera tests.

> **Safety notice:** The robot can damage itself, objects, or living beings. Always test
> in a clear area, start with low speeds, and use padding. Never leave the robot
> unattended while a script is running.

---

## Installation

### 1. Create a Python 3.8/3.9 virtual environment

The official `robomaster` package reliably installs only on Python 3.8 or 3.9.

```bash
python3.8 -m venv .venv
source .venv/bin/activate
```

If your system only has Python 3.12, install the local SDK copy instead (see below).

### 2. Install the SDK

Use the SDK that ships with this repository:

```bash
pip install -e ./RoboMaster-SDK
```

Or install from PyPI (only works on Python 3.8/3.9):

```bash
pip install robomaster
```

### 3. Install additional dependencies

```bash
pip install opencv-python opencv-contrib-python numpy
```

### 4. Verify the installation

```bash
python -c "import robomaster; print(robomaster.__version__)"
```

---

## Running the Scripts

Each script connects to the robot, performs one test, and disconnects.
All scripts default to **direct Wi-Fi AP mode** (`conn_type="ap"`).

| Script | What it does | Example |
|--------|--------------|---------|
| `test_connection_dji.py` | Check if the robot answers on the network | `python test_connection_dji.py ap` |
| `test_robot.py` | Basic chassis movement test | `python test_robot.py ap` |
| `move2.py` | Minimal chassis move example | `python move2.py` |
| `test_camera.py` | Show/save a camera frame | `python test_camera.py ap` |
| `video.py` | Stream video from the robot | `python video.py` |
| `test_gimbal.py` | Gimbal movement patterns | `python test_gimbal.py ap` |
| `test_gimbal_simple.py` | Simpler gimbal test | `python test_gimbal_simple.py ap` |
| `gimbal.py` | Low-level gimbal example | `python gimbal.py` |
| `test_led.py` | LED colors and effects | `python test_led.py ap` |
| `led.py` | Minimal LED example | `python led.py` |
| `examples/dji_sdk_basic.py` | Combined movement/gimbal/LED example | `python examples/dji_sdk_basic.py ap` |

### Connection modes

| Mode | Typical IP | When to use |
|------|------------|-------------|
| `ap` | `192.168.2.1` | Direct Wi-Fi to the robot’s access point |
| `sta` | auto / router | Robot and computer are on the same router |
| `rndis` | `192.168.42.2` | USB cable connection |

Example with USB mode:

```bash
python test_connection_dji.py rndis
```

---

## Future Project Commands

Once the planned monorepo structure is implemented (`backend/`, `frontend/`,
`robot-bridge/`), the following commands will apply. They are kept here as the
single source of truth so they can be copied into CI and onboarding docs.

### Backend (Python 3.12+)

```bash
# Install dependencies
uv sync

# Run dev server with auto-reload
uv run uvicorn app.main:app --reload --port 8000

# Tests
uv run pytest

# Lint and format
uv run ruff check . && uv run ruff format .

# Type check
uv run mypy app/
```

### Frontend (TypeScript/React)

```bash
# Install dependencies
pnpm install

# Run dev server
pnpm dev

# Build for production
pnpm build

# Tests
pnpm test

# Lint and format
pnpm lint && pnpm format
```

### Robot Bridge (Python 3.8)

```bash
cd robot-bridge/
pip install -r requirements.txt
python app/main.py
```

Or via Docker:

```bash
cd robot-bridge/
docker build -t robomastr-robot-bridge .
docker run -p 8001:8001 robomastr-robot-bridge
```

---

## Running Checks Today

Because the project has no `pyproject.toml`, `package.json`, or test runner setup yet,
the available checks are limited. You can still run:

```bash
# Basic syntax check on all Python files
python -m py_compile *.py examples/*.py

# Run a specific script
python test_connection_dji.py ap
```

Do **not** run movement scripts without a robot present and enough free space.

---

## Recommended Directory Layout (Target)

```text
robomastr/
├── backend/              # Python 3.12+ — FastAPI + Pydantic AI
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   ├── core/
│   │   └── agents/
│   ├── tests/
│   ├── pyproject.toml
│   └── uv.lock
├── robot-bridge/         # Python 3.8 ONLY — isolated robomaster SDK service
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/             # React 19 + Vite + Tailwind v4
│   ├── src/
│   ├── tests/
│   ├── package.json
│   └── pnpm-lock.yaml
└── .github/workflows/    # CI pipelines
```

See [`CLAUDE.md`](./CLAUDE.md) for the full target architecture and code conventions.

---

## Important Rules

1. **Safety first:** Max AI-controlled speed is **0.5 m/s**. Validate every robot command.
2. **Never import `robomaster` in the main backend.** Use the `robot-bridge/` HTTP service.
3. **Type safety:** `mypy --strict` (Python) and TypeScript `strict: true` (frontend).
4. **Logging:** Use structured logging (Pydantic Logfire). No `print()` in production code.
5. **Backend/frontend contracts:** Keep Pydantic models and TypeScript interfaces in sync.

---

## Repository

https://github.com/dominikbachinger124/robomastr.git
