# Implementation Plan: s1-web-control-interface

**Feature Name**: `s1-web-control-interface`  
**Based on PRD**: `.agents/prd.md`  
**Date**: 2026-07-13  

---

## 1. Overview

Build a real-time web-based control interface for the DJI RoboMaster S1 robot. Users connect a physical gamepad (Xbox/PlayStation) to their PC, open a web browser, and can control the robot while viewing a live camera feed. The system consists of three services: a React frontend, a FastAPI backend (Python 3.12+), and a robot-bridge service (Python 3.8) that interfaces with the official `robomaster` SDK.

### Key Requirements
- Real-time robot control via WebSocket with <100ms latency
- Physical gamepad support through Browser Gamepad API
- Live MJPEG video streaming from robot camera
- Safety enforcement: max speed 0.5 m/s, emergency stop, dead man's switch
- Video recording capability (video + gamepad events)
- Single user only (no multi-user support for now)

### Success Criteria
- [ ] Gamepad input translates to robot movement within 50ms
- [ ] Video stream displays at 30 FPS with <200ms latency
- [ ] Emergency stop stops robot within 100ms
- [ ] All safety limits enforced and tested
- [ ] Recording produces synchronized video + gamepad event files
- [ ] Backend and frontend pass all lint/typecheck/tests

---

## 2. Relevant Files

### Files to Create

| File | Description |
|------|-------------|
| `backend/app/main.py` | FastAPI app entry point with WebSocket and video routes |
| `backend/app/models/gamepad.py` | Pydantic models for gamepad state and commands |
| `backend/app/models/robot.py` | Pydantic models for robot state, commands, safety limits |
| `backend/app/models/recording.py` | Pydantic models for recording sessions |
| `backend/app/api/websocket.py` | WebSocket endpoint for robot control |
| `backend/app/api/video.py` | Video proxy endpoint (MJPEG stream) |
| `backend/app/api/recording.py` | REST endpoints for recording control |
| `backend/app/services/robot_control.py` | Command validation, gamepad-to-robot translation |
| `backend/app/services/robot_bridge_client.py` | HTTP client for robot-bridge service |
| `backend/app/services/recording.py` | Recording management (start/stop/save) |
| `backend/app/core/safety.py` | Safety constants, validation functions, rate limiting |
| `backend/app/core/config.py` | Application configuration (ports, limits) |
| `backend/app/core/logging.py` | Structured logging setup |
| `backend/tests/test_safety.py` | Unit tests for safety validation |
| `backend/tests/test_robot_control.py` | Unit tests for robot control service |
| `backend/pyproject.toml` | Python dependencies, project config |
| `robot-bridge/app/main.py` | FastAPI server (port 8001) for SDK integration |
| `robot-bridge/app/robot.py` | robomaster SDK wrapper |
| `robot-bridge/app/video.py` | Video capture and MJPEG streaming |
| `robot-bridge/requirements.txt` | Python 3.8 dependencies |
| `frontend/src/main.tsx` | React entry point |
| `frontend/src/App.tsx` | Main app component with routing |
| `frontend/src/components/Dashboard/RobotDashboard.tsx` | Main dashboard layout |
| `frontend/src/components/Gamepad/GamepadProvider.tsx` | Gamepad context and polling loop |
| `frontend/src/components/Gamepad/GamepadStatus.tsx` | Gamepad connection indicator |
| `frontend/src/components/Gamepad/GamepadVisualizer.tsx` | Visual display of gamepad input |
| `frontend/src/components/Video/VideoStream.tsx` | MJPEG video player component |
| `frontend/src/components/Dashboard/BatteryIndicator.tsx` | Battery level display |
| `frontend/src/components/Dashboard/SpeedIndicator.tsx` | Current speed display |
| `frontend/src/components/Safety/EmergencyStop.tsx` | Emergency stop button |
| `frontend/src/components/Recording/RecordingControls.tsx` | Start/stop recording UI |
| `frontend/src/hooks/useWebSocket.ts` | WebSocket connection hook with auto-reconnect |
| `frontend/src/hooks/useGamepad.ts` | Gamepad input hook with dead zone handling |
| `frontend/src/hooks/useRobotState.ts` | Robot state subscription hook |
| `frontend/src/hooks/useRecording.ts` | Recording control hook |
| `frontend/src/types/robot.ts` | TypeScript interfaces (mirror backend models) |
| `frontend/src/types/gamepad.ts` | Gamepad type definitions |
| `frontend/src/lib/robotCommand.ts` | Command formatting utilities |
| `frontend/src/lib/deadZone.ts` | Dead zone math utilities |
| `frontend/index.html` | HTML entry point |
| `frontend/vite.config.ts` | Vite configuration |
| `frontend/package.json` | Frontend dependencies |
| `frontend/tsconfig.json` | TypeScript strict configuration |
| `recordings/.gitkeep` | Ensure recordings directory exists |

---

## 3. Dependencies

### Backend (Python 3.12+)
```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
websockets>=13.0
httpx>=0.27.0
pydantic>=2.9.0
pydantic-settings>=2.5.0
python-multipart>=0.0.12
pytest>=8.3.0
pytest-asyncio>=0.24.0
ruff>=0.7.0
mypy>=1.13.0
```

### Robot Bridge (Python 3.8)
```
fastapi>=0.115.0
uvicorn>=0.32.0
robomaster>=0.1.0
pillow>=10.0.0
```

### Frontend
```
react@19
react-dom@19
vite@6
typescript@5.6
tailwindcss@4
@types/react@19
@types/react-dom@19
@types/w3c-gamepad@1.0.0
```

---

## 4. Step by Step Tasks

### Phase 1: Project Setup (No robot required)

#### Task 1: Create Backend Project Structure

**File**: `backend/pyproject.toml` (create new)

**Action**: Create Python project configuration with dependencies and tool settings.

**Details**:
- Define project metadata: name `robomastr-backend`, Python 3.12+ requirement
- Add all backend dependencies listed in section 3
- Configure `ruff` tool settings (line length 100, select ALL, ignore ANN101, ANN102)
- Configure `mypy` with `strict = true`
- Configure `pytest` with `asyncio_mode = auto`
- Use `setuptools` build system

**Related files**: None

---

#### Task 2: Create Backend Config Module

**File**: `backend/app/core/config.py` (create new)

**Action**: Define application settings using Pydantic Settings.

**Details**:
- Create `Settings` class inheriting from `pydantic_settings.BaseSettings`
- Fields:
  - `app_name: str = "RoboMastr Backend"`
  - `backend_port: int = 8000`
  - `robot_bridge_url: str = "http://localhost:8001"`
  - `max_linear_speed_mps: float = 0.5` (safety limit)
  - `max_angular_speed_dps: float = 180.0`
  - `max_gimbal_speed_dps: float = 90.0`
  - `commands_per_second: int = 60`
  - `dead_mans_switch_ms: int = 500`
  - `recordings_dir: str = "../recordings"`
- Use `model_config = SettingsConfigDict(env_file=".env")`

**Related files**: `backend/app/core/safety.py`

---

#### Task 3: Create Safety Module

**File**: `backend/app/core/safety.py` (create new)

**Action**: Implement safety validation functions and decorators.

**Details**:
- Import `Settings` from config
- Define constants:
  - `MAX_LINEAR_SPEED_MPS = 0.5`
  - `MAX_ANGULAR_SPEED_DPS = 180.0`
  - `MAX_GIMBAL_SPEED_DPS = 90.0`
  - `COMMANDS_PER_SECOND = 60`
  - `MIN_COMMAND_INTERVAL = 1.0 / COMMANDS_PER_SECOND`
- Create function `validate_speed(x_speed: float, y_speed: float, rotate_speed: float) -> tuple[bool, str]`:
  - Check `abs(x_speed) <= MAX_LINEAR_SPEED_MPS`
  - Check `abs(y_speed) <= MAX_LINEAR_SPEED_MPS`
  - Check `abs(rotate_speed) <= MAX_ANGULAR_SPEED_DPS`
  - Return `(True, "")` if valid, else `(False, reason)`
- Create function `validate_gimbal_speed(yaw_speed: float, pitch_speed: float) -> tuple[bool, str]`
- Create `RateLimiter` class:
  - `__init__(self, max_per_second: int = COMMANDS_PER_SECOND)`
  - `is_allowed(self, client_id: str) -> bool`: Check if command from client is within rate limit
  - Track last command time per client using `dict[str, float]`

**Related files**: `backend/app/core/config.py`, `backend/tests/test_safety.py`

---

#### Task 4: Create Gamepad Models

**File**: `backend/app/models/gamepad.py` (create new)

**Action**: Define Pydantic models for gamepad state.

**Details**:
- Create `GamepadAxes` model:
  - `left_x: float = Field(..., ge=-1.0, le=1.0)`
  - `left_y: float = Field(..., ge=-1.0, le=1.0)`
  - `right_x: float = Field(..., ge=-1.0, le=1.0)`
  - `right_y: float = Field(..., ge=-1.0, le=1.0)`
  - `left_trigger: float = Field(..., ge=0.0, le=1.0)`
  - `right_trigger: float = Field(..., ge=0.0, le=1.0)`
- Create `GamepadButtons` model:
  - `a: bool`, `b: bool`, `x: bool`, `y: bool`
  - `left_bumper: bool`, `right_bumper: bool`
  - `start: bool`, `back: bool`
- Create `GamepadState` model:
  - `axes: GamepadAxes`
  - `buttons: GamepadButtons`
  - `timestamp: int` (ms since epoch)
- Create `GamepadStateMessage` model:
  - `type: Literal["gamepad_state"] = "gamepad_state"`
  - `timestamp: int`
  - `axes: GamepadAxes`
  - `buttons: GamepadButtons`
- All models need Google-style docstrings

**Related files**: `backend/app/models/robot.py`

---

#### Task 5: Create Robot Models

**File**: `backend/app/models/robot.py` (create new)

**Action**: Define Pydantic models for robot state and commands.

**Details**:
- Create `ChassisCommand` model:
  - `x_speed_mps: float = Field(..., ge=-0.5, le=0.5)`
  - `y_speed_mps: float = Field(..., ge=-0.5, le=0.5)`
  - `rotate_speed_dps: float = Field(..., ge=-180.0, le=180.0)`
- Create `GimbalCommand` model:
  - `yaw_speed_dps: float = Field(..., ge=-90.0, le=90.0)`
  - `pitch_speed_dps: float = Field(..., ge=-90.0, le=90.0)`
- Create `RobotState` model:
  - `connected: bool`
  - `battery_percent: int = Field(..., ge=0, le=100)`
  - `wifi_signal_dbm: int`
  - `current_speed_mps: float = Field(..., ge=0.0)`
  - `gimbal_yaw_deg: float`
  - `gimbal_pitch_deg: float`
- Create `RobotStateMessage` model:
  - `type: Literal["robot_state"] = "robot_state"`
  - `timestamp: int`
  - `state: RobotState`
- Create `ErrorMessage` model:
  - `type: Literal["error"] = "error"`
  - `code: str` (enum: "SAFETY_STOP", "DISCONNECTED", "INVALID_COMMAND", "INTERNAL_ERROR")
  - `message: str`
- Create `CommandAckMessage` model:
  - `type: Literal["command_ack"] = "command_ack"`
  - `command_id: str`
  - `status: Literal["accepted", "rejected"]`
  - `reason: str | None = None`

**Related files**: `backend/app/models/gamepad.py`

---

#### Task 6: Create Robot Bridge Client

**File**: `backend/app/services/robot_bridge_client.py` (create new)

**Action**: HTTP client for communicating with robot-bridge service.

**Details**:
- Import `httpx`
- Create `RobotBridgeClient` class:
  - `__init__(self, base_url: str = "http://localhost:8001")`
  - `async def connect(self) -> dict`: POST `/connect`, return response JSON
  - `async def disconnect(self) -> dict`: POST `/disconnect`
  - `async def move_chassis(self, x: float, y: float, z: float) -> dict`: POST `/chassis/move` with JSON body
  - `async def stop_chassis(self) -> dict`: POST `/chassis/stop`
  - `async def move_gimbal(self, yaw_speed: float, pitch_speed: float) -> dict`: POST `/gimbal/move`
  - `async def fire_blaster(self) -> dict`: POST `/blaster/fire`
  - `async def get_status(self) -> dict`: GET `/status`
  - `async def get_video_stream(self) -> httpx.Response`: GET `/video/stream` (streaming response)
- Use `httpx.AsyncClient` with `timeout=10.0`
- Raise `RobotBridgeError` on connection failure
- Add structured logging for all operations

**Related files**: `backend/app/core/config.py`

---

#### Task 7: Create Robot Control Service

**File**: `backend/app/services/robot_control.py` (create new)

**Action**: Business logic for translating gamepad input to robot commands.

**Details**:
- Import `GamepadState` from `app.models.gamepad`
- Import `ChassisCommand`, `GimbalCommand` from `app.models.robot`
- Import `validate_speed` from `app.core.safety`
- Import `RobotBridgeClient` from `app.services.robot_bridge_client`
- Create `RobotControlService` class:
  - `__init__(self, bridge_client: RobotBridgeClient)`
  - `async def process_gamepad_state(self, state: GamepadState, client_id: str) -> tuple[bool, str]`:
    - Translate gamepad axes to chassis command:
      - `x_speed = -state.axes.left_y * 0.5` (invert Y axis, scale to max speed)
      - `y_speed = state.axes.left_x * 0.5`
      - `rotate_speed = state.axes.right_x * 180.0`
    - If all axes near zero (abs < 0.05), send stop command
    - Validate speed using `validate_speed`
    - If valid, send to bridge client
    - Return `(success, message)`
  - `async def handle_emergency_stop(self) -> None`: Send stop to chassis and gimbal
  - `async def handle_blaster(self, fire: bool) -> None`: Fire blaster if fire=True
- Include dead man's switch logic: if no input received for 500ms, auto-stop

**Related files**: `backend/app/models/gamepad.py`, `backend/app/models/robot.py`, `backend/app/core/safety.py`, `backend/app/services/robot_bridge_client.py`

---

#### Task 8: Create Recording Service

**File**: `backend/app/services/recording.py` (create new)

**Action**: Manage video and gamepad event recording.

**Details**:
- Import `pathlib`, `datetime`, `json`, `asyncio`
- Create `RecordingSession` class:
  - `__init__(self, recordings_dir: str)`
  - `start(self) -> str`: Create timestamped directory, return session ID
  - `stop(self) -> str`: Finalize recording, return path to session directory
  - `write_video_frame(self, frame: bytes, timestamp: int) -> None`: Append JPEG frame to file
  - `write_gamepad_event(self, event: dict, timestamp: int) -> None`: Append to JSONL file
- Create `RecordingManager` class:
  - `__init__(self, recordings_dir: str = "../recordings")`
  - `start_recording(self) -> str`: Start new session
  - `stop_recording(self) -> str | None`: Stop current session
  - `is_recording(self) -> bool`
  - `get_current_session(self) -> RecordingSession | None`
- Video frames saved as individual JPEGs in `recordings/YYYY-MM-DD_HH-MM-SS/frames/`
- Gamepad events saved as `recordings/YYYY-MM-DD_HH-MM-SS/events.jsonl` (JSON Lines format)

**Related files**: `backend/app/api/recording.py`

---

#### Task 9: Create WebSocket API

**File**: `backend/app/api/websocket.py` (create new)

**Action**: WebSocket endpoint for real-time robot control.

**Details**:
- Import `fastapi.WebSocket`, `WebSocketDisconnect`
- Import `RobotControlService` from `app.services.robot_control`
- Import `GamepadStateMessage`, `GamepadState` from `app.models.gamepad`
- Import `RobotStateMessage`, `ErrorMessage` from `app.models.robot`
- Create `RobotWebSocket` class:
  - `__init__(self, control_service: RobotControlService)`
  - `async def handle_connection(self, websocket: WebSocket) -> None`:
    - Accept connection
    - Start background task for robot state broadcasting (every 1 second)
    - Loop: receive JSON messages, parse based on `type` field
    - Handle `gamepad_state`: call `control_service.process_gamepad_state`
    - Handle `get_state`: send current state
    - Handle `command`: execute command (move, stop, etc.)
    - On disconnect: cleanup, stop any ongoing movement
  - `async def broadcast_state(self, websocket: WebSocket) -> None`: Send robot state periodically
- Use `ConnectionManager` to track active connections (only 1 allowed)
- Handle errors gracefully: send `ErrorMessage` to client

**Related files**: `backend/app/services/robot_control.py`, `backend/app/models/gamepad.py`, `backend/app/models/robot.py`

---

#### Task 10: Create Video API

**File**: `backend/app/api/video.py` (create new)

**Action**: Video proxy endpoint for MJPEG streaming.

**Details**:
- Import `fastapi.APIRouter`, `StreamingResponse`
- Import `RobotBridgeClient` from `app.services.robot_bridge_client`
- Create router: `router = APIRouter(prefix="/api/video", tags=["video"])`
- Create endpoint `@router.get("/stream")`:
  - Connect to robot-bridge video stream using `bridge_client.get_video_stream()`
  - Return `StreamingResponse` with `media_type="multipart/x-mixed-replace; boundary=--frame_boundary"`
  - Stream content directly from bridge to client
- Handle disconnections gracefully
- Include CORS headers for frontend access

**Related files**: `backend/app/services/robot_bridge_client.py`

---

#### Task 11: Create Recording API

**File**: `backend/app/api/recording.py` (create new)

**Action**: REST endpoints for recording control.

**Details**:
- Import `fastapi.APIRouter`
- Import `RecordingManager` from `app.services.recording`
- Create router: `router = APIRouter(prefix="/api/recording", tags=["recording"])`
- Create endpoint `@router.post("/start")`:
  - Call `recording_manager.start_recording()`
  - Return `{"status": "started", "session_id": session_id}`
- Create endpoint `@router.post("/stop")`:
  - Call `recording_manager.stop_recording()`
  - Return `{"status": "stopped", "path": path}`
- Create endpoint `@router.get("/status")`:
  - Return `{"is_recording": bool, "session_id": str | None}`

**Related files**: `backend/app/services/recording.py`

---

#### Task 12: Create Main Backend Entry Point

**File**: `backend/app/main.py` (create new)

**Action**: FastAPI application entry point.

**Details**:
- Import `FastAPI`
- Import websocket router, video router, recording router
- Create `app = FastAPI(title="RoboMastr Backend", version="0.1.0")`
- Include routers
- Add CORS middleware for frontend (allow `http://localhost:5173`)
- Add WebSocket route: `@app.websocket("/api/robot/control")`
- Startup event: initialize services
- Shutdown event: cleanup connections

**Related files**: All backend API and service files

---

### Phase 2: Robot Bridge (Requires Python 3.8)

#### Task 13: Create Robot Bridge Service

**File**: `robot-bridge/app/main.py` (create new)

**Action**: FastAPI server that wraps the robomaster SDK.

**Details**:
- Import `FastAPI`, `StreamingResponse`
- Import `RobotController` from `app.robot`
- Import `VideoCapture` from `app.video`
- Create `app = FastAPI(title="Robot Bridge", version="0.1.0")`
- Endpoints:
  - `POST /connect`: Initialize robot with `conn_type` (default "ap"). Return robot info.
  - `POST /disconnect`: Close robot connection
  - `POST /chassis/move`: Body `{"x": float, "y": float, "z": float}`. Call `robot.chassis.drive_speed(x, y, z)`.
  - `POST /chassis/stop`: Call `robot.chassis.drive_speed(0, 0, 0)`
  - `POST /gimbal/move`: Body `{"yaw_speed": float, "pitch_speed": float}`. Call `robot.gimbal.drive_speed(pitch_speed, yaw_speed)`.
  - `POST /blaster/fire`: Call `robot.blaster.fire()`
  - `GET /status`: Return robot status (battery, WiFi signal, etc.)
  - `GET /video/stream`: Return MJPEG stream from `VideoCapture`
- Global state: single `RobotController` instance
- Handle SDK exceptions and return HTTP 400/500 with details

**Related files**: `robot-bridge/app/robot.py`, `robot-bridge/app/video.py`

---

#### Task 14: Create Robot SDK Wrapper

**File**: `robot-bridge/app/robot.py` (create new)

**Action**: Wrapper around the robomaster SDK.

**Details**:
- Import `robomaster.robot`
- Create `RobotController` class:
  - `__init__(self)`
  - `connect(self, conn_type: str = "ap") -> dict`: Initialize robot, return `{"sn": str, "version": str}`
  - `disconnect(self) -> None`: Call `robot.close()`
  - `move_chassis(self, x: float, y: float, z: float) -> None`: Call `chassis.drive_speed(x, y, z)`
  - `stop_chassis(self) -> None`: Call `chassis.drive_speed(0, 0, 0)`
  - `move_gimbal(self, yaw_speed: float, pitch_speed: float) -> None`: Call `gimbal.drive_speed(pitch_speed, yaw_speed)`
  - `fire_blaster(self) -> None`: Call `blaster.fire()`
  - `get_status(self) -> dict`: Return battery, wifi signal, etc.
- Maintain singleton instance in module scope
- Thread-safe (SDK may not be async)

**Related files**: `robot-bridge/app/main.py`

---

#### Task 15: Create Video Capture Module

**File**: `robot-bridge/app/video.py` (create new)

**Action**: Capture video frames from robot camera.

**Details**:
- Import `robomaster.camera`, `io`, `threading`, `queue`
- Create `VideoCapture` class:
  - `__init__(self, robot_controller)`
  - `start(self) -> None`: Subscribe to camera feed using `robot.camera.start_video_stream(callback)`
  - `stop(self) -> None`: Stop video stream
  - `get_frame(self) -> bytes | None`: Return latest JPEG frame from queue
  - `generate_mjpeg(self) -> Generator[bytes, None, None]`: Yield MJPEG multipart frames for streaming
- Camera settings: resolution 640x480, bitrate moderate
- Use `queue.Queue(maxsize=5)` to buffer frames, drop old ones if full

**Related files**: `robot-bridge/app/main.py`, `robot-bridge/app/robot.py`

---

### Phase 3: Frontend

#### Task 16: Setup Frontend Project

**File**: `frontend/package.json` (create new)

**Action**: Create frontend package configuration.

**Details**:
- `name`: `robomastr-frontend`
- `version`: `0.1.0`
- `type`: `module`
- Dependencies:
  - `react: ^19.0.0`
  - `react-dom: ^19.0.0`
  - `vite: ^6.0.0`
  - `@vitejs/plugin-react: ^4.3.0`
  - `typescript: ^5.6.0`
  - `@types/react: ^19.0.0`
  - `@types/react-dom: ^19.0.0`
  - `@types/w3c-gamepad: ^1.0.0`
  - `tailwindcss: ^4.0.0`
  - `@tailwindcss/vite: ^4.0.0`
  - `eslint: ^9.0.0`
  - `@eslint/js: ^9.0.0`
  - `typescript-eslint: ^8.0.0`
  - `globals: ^15.0.0`
- Scripts:
  - `dev`: `vite`
  - `build`: `tsc && vite build`
  - `lint`: `eslint .`
  - `typecheck`: `tsc --noEmit`
  - `preview`: `vite preview`

**Related files**: `frontend/tsconfig.json`, `frontend/vite.config.ts`

---

#### Task 17: Create TypeScript Config

**File**: `frontend/tsconfig.json` (create new)

**Action**: Strict TypeScript configuration.

**Details**:
- `compilerOptions`:
  - `target: "ES2022"`
  - `lib: ["ES2022", "DOM", "DOM.Iterable"]`
  - `module: "ESNext"`
  - `moduleResolution: "bundler"`
  - `strict: true` (enable all strict options)
  - `noUnusedLocals: true`
  - `noUnusedParameters: true`
  - `noImplicitReturns: true`
  - `noFallthroughCasesInSwitch: true`
  - `esModuleInterop: true`
  - `skipLibCheck: true`
  - `forceConsistentCasingInFileNames: true`
  - `jsx: "react-jsx"`
  - `baseUrl: "."`
  - `paths: { "@/*": ["src/*"] }`
- Include: `src/**/*`
- Exclude: `node_modules`, `dist`

**Related files**: `frontend/vite.config.ts`

---

#### Task 18: Create Vite Config

**File**: `frontend/vite.config.ts` (create new)

**Action**: Vite configuration with path aliases.

**Details**:
- Import `defineConfig` from `vite`
- Import `react` from `@vitejs/plugin-react`
- Import `tailwindcss` from `@tailwindcss/vite`
- Export default with:
  - `plugins: [react(), tailwindcss()]`
  - `resolve.alias: { "@": "/src" }`
  - `server.port: 5173`
  - `server.proxy: { "/api": "http://localhost:8000", "/ws": { target: "ws://localhost:8000", ws: true } }`

**Related files**: `frontend/tsconfig.json`

---

#### Task 19: Create Robot Types

**File**: `frontend/src/types/robot.ts` (create new)

**Action**: TypeScript interfaces mirroring backend models.

**Details**:
- `interface GamepadAxes`
- `interface GamepadButtons`
- `interface GamepadState`
- `interface GamepadStateMessage`
- `interface RobotState`
- `interface RobotStateMessage`
- `interface ErrorMessage`
- `interface CommandAckMessage`
- `interface WebSocketMessage` union type of all message types
- All fields exactly match backend Pydantic models
- Export all interfaces

**Related files**: `frontend/src/hooks/useWebSocket.ts`

---

#### Task 20: Create WebSocket Hook

**File**: `frontend/src/hooks/useWebSocket.ts` (create new)

**Action**: Custom hook for WebSocket connection management.

**Details**:
- `import { useState, useEffect, useRef, useCallback } from "react"`
- `import type { WebSocketMessage, RobotStateMessage, ErrorMessage } from "@/types/robot"`
- Export `function useWebSocket(url: string)`:
  - `isConnected: boolean`
  - `robotState: RobotStateMessage | null`
  - `error: ErrorMessage | null`
  - `sendMessage: (msg: WebSocketMessage) => void`
  - `lastMessage: WebSocketMessage | null`
- Implementation:
  - Use `useRef<WebSocket | null>()` for socket
  - Auto-reconnect with exponential backoff (max 5s delay)
  - Parse incoming messages based on `type` field
  - Heartbeat/ping every 30 seconds
  - Clean disconnect on unmount

**Related files**: `frontend/src/types/robot.ts`

---

#### Task 21: Create Gamepad Hook

**File**: `frontend/src/hooks/useGamepad.ts` (create new)

**Action**: Custom hook for gamepad input polling.

**Details**:
- `import { useState, useEffect, useRef, useCallback } from "react"`
- `import type { GamepadState, GamepadAxes, GamepadButtons } from "@/types/robot"`
- Export `function useGamepad()`:
  - `gamepadState: GamepadState | null`
  - `isConnected: boolean`
  - `gamepadIndex: number | null`
- Implementation:
  - Poll `navigator.getGamepads()` at 60fps using `requestAnimationFrame`
  - Find first connected standard gamepad
  - Map gamepad axes to `GamepadAxes` (apply dead zone)
  - Map gamepad buttons to `GamepadButtons`
  - Dead zone function: `Math.abs(val) < 0.15 ? 0 : (val - Math.sign(val) * 0.15) / 0.85`
  - Standard mapping: axes[0]=left_x, axes[1]=left_y, axes[2]=right_x, axes[3]=right_y

**Related files**: `frontend/src/types/robot.ts`, `frontend/src/components/Gamepad/GamepadProvider.tsx`

---

#### Task 22: Create Gamepad Provider

**File**: `frontend/src/components/Gamepad/GamepadProvider.tsx` (create new)

**Action**: React context for gamepad state, sends input to backend via WebSocket.

**Details**:
- `import { createContext, useContext, useEffect, ReactNode } from "react"`
- `import { useGamepad } from "@/hooks/useGamepad"`
- `import { useWebSocket } from "@/hooks/useWebSocket"`
- Create `GamepadContext` with `gamepadState`, `isConnected`
- Export `function GamepadProvider({ children, wsUrl }: { children: ReactNode; wsUrl: string })`:
  - Use `useGamepad()` to get input
  - Use `useWebSocket(wsUrl)` for backend connection
  - `useEffect`: when gamepadState changes, send `gamepad_state` message via WebSocket
  - Include timestamp in each message: `Date.now()`
  - Only send if WebSocket is connected
- Export `function useGamepadContext()` for consumers

**Related files**: `frontend/src/hooks/useGamepad.ts`, `frontend/src/hooks/useWebSocket.ts`

---

#### Task 23: Create Video Stream Component

**File**: `frontend/src/components/Video/VideoStream.tsx` (create new)

**Action**: Display MJPEG video stream.

**Details**:
- `import { useRef, useEffect, useState } from "react"`
- Export `function VideoStream({ src }: { src: string })`:
  - `imgRef = useRef<HTMLImageElement>(null)`
  - Set `img.src` to MJPEG stream URL
  - Display connection status overlay
  - Show loading state until first frame
  - Handle errors (broken stream)
- Use `img` element with `src={src}` (browser handles MJPEG natively)
- Style with Tailwind: full container width, maintain aspect ratio

**Related files**: `frontend/src/components/Dashboard/RobotDashboard.tsx`

---

#### Task 24: Create Dashboard Components

**File**: `frontend/src/components/Dashboard/RobotDashboard.tsx` (create new)

**Action**: Main dashboard layout.

**Details**:
- Import `VideoStream`, `GamepadStatus`, `BatteryIndicator`, `SpeedIndicator`, `EmergencyStop`, `RecordingControls`
- Export `function RobotDashboard()`:
  - Layout: video stream on left (2/3 width), controls on right (1/3 width)
  - Controls panel:
    - Connection status (WebSocket + Robot)
    - Battery indicator (percentage + icon)
    - Speed indicator (current m/s)
    - Gamepad status (connected/disconnected + visualizer)
    - Emergency stop button (large red)
    - Recording controls (start/stop)
  - Use Tailwind grid layout
  - Responsive: stack on small screens

**Related files**: All dashboard sub-components

---

#### Task 25: Create Supporting UI Components

**Files**:
- `frontend/src/components/Gamepad/GamepadStatus.tsx`
- `frontend/src/components/Gamepad/GamepadVisualizer.tsx`
- `frontend/src/components/Dashboard/BatteryIndicator.tsx`
- `frontend/src/components/Dashboard/SpeedIndicator.tsx`
- `frontend/src/components/Safety/EmergencyStop.tsx`
- `frontend/src/components/Recording/RecordingControls.tsx`

**Action**: Create all supporting UI components.

**Details**:
- `GamepadStatus`: Show connected/disconnected, button count, mapping
- `GamepadVisualizer`: Visual bars for each axis, colored buttons
- `BatteryIndicator`: Battery icon + percentage, color changes (green >50, yellow 20-50, red <20)
- `SpeedIndicator`: Speedometer-style display, current speed in m/s
- `EmergencyStop`: Large red button, sends emergency stop command via WebSocket, confirmation dialog
- `RecordingControls`: Start/Stop recording buttons, show recording status (red dot when active), display recording duration

**Related files**: `frontend/src/hooks/useWebSocket.ts`, `frontend/src/types/robot.ts`

---

#### Task 26: Create App Entry Point

**File**: `frontend/src/App.tsx` (create new)

**Action**: Main application component.

**Details**:
- Import `GamepadProvider` from `@/components/Gamepad/GamepadProvider`
- Import `RobotDashboard` from `@/components/Dashboard/RobotDashboard`
- Export `function App()`:
  - Wrap in `GamepadProvider` with `wsUrl="ws://localhost:8000/api/robot/control"`
  - Render `RobotDashboard`
  - Show error boundary for WebSocket errors

**Related files**: `frontend/src/main.tsx`

---

#### Task 27: Create HTML Entry Point

**File**: `frontend/index.html` (create new)

**Action**: HTML template for Vite.

**Details**:
- Standard HTML5 boilerplate
- `title`: `RoboMastr S1 Control`
- Script: `src="/src/main.tsx" type="module"`
- Meta viewport tag for responsiveness

**Related files**: `frontend/src/main.tsx`

---

### Phase 4: Testing

#### Task 28: Create Backend Safety Tests

**File**: `backend/tests/test_safety.py` (create new)

**Action**: Unit tests for safety validation.

**Details**:
- Import `pytest`
- Import `validate_speed`, `validate_gimbal_speed`, `RateLimiter` from `app.core.safety`
- Tests:
  - `test_validate_speed_within_limits`: assert valid speed passes
  - `test_validate_speed_exceeds_linear`: assert 0.6 m/s rejected
  - `test_validate_speed_exceeds_angular`: assert 200 dps rejected
  - `test_rate_limiter_allows_first`: first command allowed
  - `test_rate_limiter_blocks_spam`: command within 16ms blocked

**Related files**: `backend/app/core/safety.py`

---

#### Task 29: Create Backend Robot Control Tests

**File**: `backend/tests/test_robot_control.py` (create new)

**Action**: Unit tests for robot control service.

**Details**:
- Import `pytest`, `pytest-asyncio`
- Import `RobotControlService` from `app.services.robot_control`
- Import `GamepadState` from `app.models.gamepad`
- Mock `RobotBridgeClient`
- Tests:
  - `test_process_gamepad_stop`: all axes zero sends stop
  - `test_process_gamepad_move`: left stick forward sends positive x_speed
  - `test_process_gamepad_respects_dead_zone`: small inputs result in stop
  - `test_emergency_stop`: sends stop to chassis and gimbal

**Related files**: `backend/app/services/robot_control.py`

---

### Phase 5: Integration

#### Task 30: Create Recordings Directory

**File**: `recordings/.gitkeep` (create new)

**Action**: Ensure recordings directory exists in repo.

**Details**:
- Create empty file `.gitkeep`
- Add `recordings/*` to `.gitignore` (keep directory, ignore contents)

**Related files**: `.gitignore`

---

## 5. Testing Strategy

### Unit Tests
- **Backend**: `pytest` with `pytest-asyncio` for async service tests
- **Frontend**: React Testing Library for component tests (optional for initial version)

### Integration Tests
- WebSocket message serialization/deserialization
- Gamepad input → robot command translation (mock bridge)
- Video stream proxy (mock MJPEG source)

### Manual Testing (requires physical robot)
1. Connect to robot WiFi
2. Start robot-bridge: `python3.8 robot-bridge/app/main.py`
3. Start backend: `uv run uvicorn app.main:app --port 8000`
4. Start frontend: `pnpm dev`
5. Connect gamepad to PC
6. Verify: video stream appears, gamepad input moves robot, emergency stop works
7. Test recording: start/stop recording, verify files created

---

## 6. Validation Commands

After implementation, run in order:

```bash
# --- Backend ---
cd backend

# Install dependencies
uv sync

# Linting
uv run ruff check app/ tests/

# Type checking
uv run mypy app/

# Tests
uv run pytest tests/

# --- Robot Bridge ---
cd robot-bridge

# Install dependencies (Python 3.8)
pip3.8 install -r requirements.txt

# Linting
python3.8 -m ruff check app/

# --- Frontend ---
cd frontend

# Install dependencies
pnpm install

# Type checking
pnpm typecheck

# Linting
pnpm lint

# Build check
pnpm build
```

---

## 7. Integration Notes

### How This Feature Connects to Existing Code
- This is a new feature that creates the `backend/`, `frontend/`, and `robot-bridge/` directories from scratch
- Existing `examples/` and `reference/` directories are for documentation only
- The `robomaster` SDK in `RoboMaster-SDK/` is used by `robot-bridge/`

### Potential Breaking Changes
- None (new feature, no existing code to break)

### Documentation Updates Required
- Update `CLAUDE.md` if architecture changes
- Add `README.md` in project root with setup instructions

### Startup Sequence
1. Connect PC to robot WiFi (or robot to router)
2. `cd robot-bridge && python3.8 -m uvicorn app.main:app --port 8001`
3. `cd backend && uv run uvicorn app.main:app --port 8000`
4. `cd frontend && pnpm dev`
5. Open `http://localhost:5173` in browser
6. Connect gamepad to PC
7. Click "Connect to Robot" in UI

---

## Confirmation

- ✅ Feature name created: `s1-web-control-interface`
- ✅ Plan saved to `plans/s1-web-control-interface.md`
- ✅ All tasks are explicit with file paths
- ✅ Validation commands are exact
- ✅ Another agent could execute this without context

**Next step**: Run `/execute plans/s1-web-control-interface.md` to implement this feature