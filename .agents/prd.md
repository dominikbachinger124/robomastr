# Product Requirements Document: RoboMaster S1 Web Control Interface

**Feature Name**: `s1-web-control-interface`  
**Status**: Draft  
**Date**: 2026-07-13  
**Author**: AI Assistant  

---

## 1. Executive Summary

This PRD defines a real-time web-based control interface for the DJI RoboMaster S1 robot. The system will enable users to control the robot using a physical gamepad (Xbox/PlayStation) while viewing a live video stream from the robot's camera, all through a modern web browser.

### Key Value Propositions
- **Real-time control**: Sub-100ms latency for responsive robot movement
- **Universal compatibility**: Works with any USB/Bluetooth gamepad via Browser Gamepad API
- **Live video**: Stream robot camera feed directly to the browser
- **Safety-first**: Built-in speed limits, emergency stop, and command validation
- **Modern tech stack**: React 19 + FastAPI + WebSocket for real-time bidirectional communication

---

## 2. Architecture Decisions

### 2.1 Robot Bridge Integration: **REQUIRED**

**Decision**: YES, we will implement a dedicated `robot-bridge` service.

**Rationale**:
- The `robomaster` SDK requires Python 3.8
- Main backend runs Python 3.12+ (Pydantic v2, modern async features)
- Isolating the SDK prevents dependency conflicts and SDK limitations from affecting the main backend
- The bridge pattern allows for future extensibility (multiple robots, simulation mode)

**Architecture Flow**:
```
┌─────────────┐     WebSocket      ┌──────────────┐     HTTP/REST    ┌──────────────┐     SDK Calls    ┌─────────┐
│   Browser   │ ◄────────────────► │   Backend    │ ◄──────────────► │ Robot Bridge │ ◄──────────────► │    S1   │
│  (React)    │   (FastAPI WS)    │  (Python 3.12)│                 │ (Python 3.8) │                 │  Robot  │
└─────────────┘                   └──────────────┘                  └──────────────┘                 └─────────┘
       │                                  │                                │
       │    ┌─────────────────────┐     │    ┌─────────────────────┐   │
       └───►│  Gamepad API          │     └───►│  Video Proxy/Stream   │   │
            │  (Local Input)        │          │  (MJPEG/HTTP)        │   │
            └─────────────────────┘          └─────────────────────┘   │
```

### 2.2 Real-Time Communication: **WebSocket**

**Decision**: WebSocket for all control commands; MJPEG stream for video.

**Rationale**:
- WebSocket provides persistent, low-latency bidirectional communication
- Reduces HTTP overhead for high-frequency control commands (60fps gamepad input)
- Native support in both FastAPI (Starlette) and React
- Simpler than WebRTC for this point-to-point scenario

**Video Streaming Approach**:
- **MJPEG over HTTP**: Most compatible with robomaster SDK (provides frames as JPEG)
- Stream URL: `http://backend:8000/api/video/stream`
- Backend acts as proxy between robot bridge and frontend
- Alternative: WebSocket binary frames for lower latency (Phase 2 enhancement)

### 2.3 Gamepad Input Handling: **Browser Gamepad API**

**Decision**: Gamepad input captured in browser, sent via WebSocket to backend.

**Rationale**:
- Browser Gamepad API is mature and supports Xbox, PlayStation, and generic controllers
- No drivers needed for standard USB/Bluetooth gamepads
- Input smoothing and dead-zone handling can be done in browser or backend
- Same physical PC setup means no network latency concerns

**Control Mapping** (Default):
| Gamepad Input | Robot Action |
|--------------|--------------|
| Left Stick X/Y | Chassis movement (forward/back/left/right) |
| Right Stick X | Gimbal rotation (left/right) |
| Right Stick Y | Gimbal pitch (up/down) |
| Right Trigger | Fire blaster (hold) |
| Left Trigger | Zoom camera |
| Start Button | Emergency stop |
| A/B/X/Y | Custom actions (TBD) |

---

## 3. System Components

### 3.1 Backend (Python 3.12+, FastAPI)

**Responsibilities**:
- WebSocket connection management (multiple clients, single robot)
- Command validation and safety enforcement
- Gamepad command translation to robot commands
- Video stream proxy
- Robot state management (battery, connection status, current speed)

**Key Files to Create**:
- `backend/app/api/websocket.py` - WebSocket endpoint for robot control
- `backend/app/services/robot_control.py` - Business logic for command validation
- `backend/app/services/robot_bridge_client.py` - HTTP client for robot-bridge
- `backend/app/models/gamepad.py` - Pydantic models for gamepad input
- `backend/app/models/robot.py` - Robot state and command models
- `backend/app/core/safety.py` - Safety limits and validation
- `backend/app/core/video_stream.py` - Video proxy and streaming

### 3.2 Robot Bridge (Python 3.8, Isolated Service)

**Responsibilities**:
- Direct robomaster SDK integration
- Video frame capture and forwarding
- Chassis and gimbal command execution
- Robot connection management (WiFi)

**Key Files to Create**:
- `robot-bridge/app/main.py` - FastAPI server (port 8001)
- `robot-bridge/app/robot.py` - SDK wrapper and control logic
- `robot-bridge/app/video.py` - Video capture and streaming
- `robot-bridge/requirements.txt` - Python 3.8 dependencies

### 3.3 Frontend (React 19 + TypeScript + Tailwind v4)

**Responsibilities**:
- Gamepad input polling and capture
- WebSocket connection to backend
- Live video feed display
- Control UI (connection status, battery, speed indicators)
- Emergency stop button

**Key Files to Create**:
- `frontend/src/components/Gamepad/GamepadProvider.tsx` - Gamepad context and polling
- `frontend/src/components/Video/VideoStream.tsx` - MJPEG video player
- `frontend/src/components/Dashboard/RobotDashboard.tsx` - Main dashboard
- `frontend/src/components/Safety/EmergencyStop.tsx` - Emergency controls
- `frontend/src/hooks/useWebSocket.ts` - WebSocket connection hook
- `frontend/src/hooks/useGamepad.ts` - Gamepad input hook
- `frontend/src/types/robot.ts` - TypeScript interfaces (mirror backend models)
- `frontend/src/lib/robotCommand.ts` - Command formatting utilities

---

## 4. API Contracts

### 4.1 WebSocket Protocol (Client ↔ Backend)

**Connection**: `ws://backend:8000/api/robot/control`

**Client → Server Messages**:
```typescript
// Gamepad State (sent at 60fps when gamepad connected)
interface GamepadStateMessage {
  type: 'gamepad_state';
  timestamp: number;  // ms since epoch
  axes: {             // Normalized -1.0 to 1.0
    left_x: number;
    left_y: number;
    right_x: number;
    right_y: number;
    left_trigger: number;   // 0.0 to 1.0
    right_trigger: number;  // 0.0 to 1.0
  };
  buttons: {
    a: boolean;
    b: boolean;
    x: boolean;
    y: boolean;
    left_bumper: boolean;
    right_bumper: boolean;
    start: boolean;
    back: boolean;
  };
}

// Manual Command (for UI buttons)
interface CommandMessage {
  type: 'command';
  action: 'move_forward' | 'move_backward' | 'turn_left' | 'turn_right' | 'stop';
  params?: {
    distance?: number;  // mm
    speed?: number;     // m/s (0.0-0.5)
    angle?: number;     // degrees
  };
}

// Request robot state
interface GetStateMessage {
  type: 'get_state';
}
```

**Server → Client Messages**:
```typescript
// Robot state update (sent every 1s or on change)
interface RobotStateMessage {
  type: 'robot_state';
  timestamp: number;
  state: {
    connected: boolean;
    battery_percent: number;      // 0-100
    wifi_signal: number;          // dBm
    current_speed_mps: number;    // Current movement speed
    gimbal_angle: {
      yaw: number;    // degrees
      pitch: number;  // degrees
    };
  };
}

// Command acknowledgment
interface CommandAckMessage {
  type: 'command_ack';
  command_id: string;
  status: 'accepted' | 'rejected';
  reason?: string;  // If rejected
}

// Error message
interface ErrorMessage {
  type: 'error';
  code: 'SAFETY_STOP' | 'DISCONNECTED' | 'INVALID_COMMAND' | 'INTERNAL_ERROR';
  message: string;
}
```

### 4.2 REST API (Backend ↔ Robot Bridge)

**Base URL**: `http://localhost:8001`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/connect` | POST | Connect to robot (WiFi) |
| `/disconnect` | POST | Disconnect from robot |
| `/chassis/move` | POST | Move chassis: `{x: m/s, y: m/s, z: deg/s}` |
| `/chassis/stop` | POST | Emergency stop |
| `/gimbal/move` | POST | Move gimbal: `{yaw: deg, pitch: deg, speed: deg/s}` |
| `/blaster/fire` | POST | Fire blaster |
| `/video/stream` | GET | MJPEG video stream |
| `/status` | GET | Robot status: battery, WiFi, etc. |

### 4.3 Video Stream

**URL**: `http://backend:8000/api/video/stream` (proxied from robot-bridge)

**Format**: MJPEG over HTTP (multipart/x-mixed-replace)
- Resolution: 640x480 (configurable)
- Frame rate: 30 FPS (configurable)
- Compression: JPEG quality 80

---

## 5. Safety Requirements

### 5.1 Speed Limits (Hardcoded)

```python
MAX_LINEAR_SPEED_MPS = 0.5      # m/s - AI/Remote control limit
MAX_ANGULAR_SPEED_DPS = 180     # degrees/s
MAX_GIMBAL_SPEED_DPS = 90       # degrees/s
```

### 5.2 Validation Rules

- All commands validated before execution
- Reject commands exceeding speed limits
- Reject movement commands if robot not connected
- Rate limiting: max 60 commands/sec per client
- Emergency stop: immediate execution, clears all pending commands

### 5.3 Dead Man's Switch

- If no gamepad input for 500ms, automatically stop chassis
- Prevents runaway robot if gamepad disconnects

---

## 6. File Structure

```
robomastr/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── websocket.py          # WebSocket endpoint
│   │   │   └── video.py              # Video proxy endpoint
│   │   ├── models/
│   │   │   ├── gamepad.py            # GamepadState, etc.
│   │   │   └── robot.py              # RobotState, Command models
│   │   ├── services/
│   │   │   ├── robot_control.py      # Command validation & logic
│   │   │   └── robot_bridge_client.py # HTTP client for bridge
│   │   ├── core/
│   │   │   ├── safety.py             # Safety limits & validation
│   │   │   └── video_stream.py       # Video proxy handler
│   │   └── main.py                   # FastAPI app entry
│   ├── pyproject.toml
│   └── uv.lock
├── robot-bridge/
│   ├── app/
│   │   ├── main.py                   # FastAPI server (port 8001)
│   │   ├── robot.py                  # robomaster SDK wrapper
│   │   └── video.py                  # Video capture & streaming
│   ├── requirements.txt              # Python 3.8 only
│   └── Dockerfile                    # Python 3.8 base image
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Gamepad/
│   │   │   │   ├── GamepadProvider.tsx
│   │   │   │   ├── GamepadStatus.tsx
│   │   │   │   └── GamepadVisualizer.tsx
│   │   │   ├── Video/
│   │   │   │   └── VideoStream.tsx
│   │   │   ├── Dashboard/
│   │   │   │   ├── RobotDashboard.tsx
│   │   │   │   ├── BatteryIndicator.tsx
│   │   │   │   └── SpeedIndicator.tsx
│   │   │   └── Safety/
│   │   │       └── EmergencyStop.tsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useGamepad.ts
│   │   │   └── useRobotState.ts
│   │   ├── types/
│   │   │   └── robot.ts              # Mirror of backend models
│   │   ├── lib/
│   │   │   └── robotCommand.ts
│   │   └── App.tsx
│   ├── package.json
│   └── pnpm-lock.yaml
└── .agents/
    └── prd.md                        # This file
```

---

## 7. Implementation Plan

### Phase 1: Foundation (Week 1)
- [ ] Set up robot-bridge service with Python 3.8
- [ ] Implement basic robot connection and movement
- [ ] Create video capture from robomaster SDK
- [ ] Test robot-bridge API endpoints

### Phase 2: Backend (Week 1-2)
- [ ] Implement WebSocket endpoint with connection management
- [ ] Create robot bridge HTTP client
- [ ] Implement safety validation layer
- [ ] Add video proxy endpoint
- [ ] Write tests for services

### Phase 3: Frontend Core (Week 2)
- [ ] Set up React project with TypeScript strict mode
- [ ] Implement gamepad API hooks and provider
- [ ] Create WebSocket connection hook
- [ ] Build video stream component

### Phase 4: Dashboard & Safety (Week 3)
- [ ] Build main dashboard layout
- [ ] Implement robot status indicators
- [ ] Add emergency stop UI
- [ ] Gamepad visualizer for debugging

### Phase 5: Integration & Testing (Week 3-4)
- [ ] End-to-end testing with physical robot
- [ ] Latency optimization
- [ ] Safety testing (emergency stop, disconnections)
- [ ] Documentation

---

## 8. Testing Strategy

### 8.1 Unit Tests

**Backend**:
- `test_safety.py`: Validate speed limits, command rejection
- `test_robot_control.py`: Mock robot bridge, test command translation
- `test_websocket.py`: Test connection management, message handling

**Frontend**:
- `useGamepad.test.ts`: Mock gamepad API, test input mapping
- `useWebSocket.test.ts`: Mock WebSocket, test reconnection logic
- `VideoStream.test.tsx`: Test MJPEG player

### 8.2 Integration Tests

- Robot bridge → SDK integration (requires physical robot)
- Backend → Robot bridge HTTP communication
- Frontend → Backend WebSocket communication

### 8.3 Safety Tests

- Emergency stop response time < 100ms
- Dead man's switch triggers after 500ms
- Speed limit enforcement (attempt to exceed 0.5 m/s)
- Command rejection when robot disconnected

---

## 9. Validation Commands

After implementation, run these commands:

```bash
# Backend
cd backend
uv run ruff check .
uv run mypy app/
uv run pytest

# Robot Bridge
cd robot-bridge
python3.8 -m ruff check .
python3.8 -m pytest

# Frontend
cd frontend
pnpm lint
pnpm typecheck
pnpm test

# Integration (requires robot)
# WebSocket latency test: < 100ms round-trip
# Video stream: 30 FPS, no dropped frames
# Gamepad → Robot command: < 50ms latency
```

---

## 10. Decisions Log

| Question | Decision |
|----------|----------|
| WiFi Connection | Direct connection established before robot communication. No stored credentials. |
| Multi-user | Single user only for initial implementation. |
| Recording | Yes - record gameplay/video sessions for later playback. |
| Mobile | Not required. PC with gamepad is the only supported setup. |

## 11. Recording Feature Specification

### Requirements
- Record video stream + gamepad input events to a file
- Synchronized playback: video + gamepad overlay
- Start/stop recording from dashboard UI
- File format: MP4 for video, JSON for gamepad events
- Storage: local filesystem in `recordings/` directory

### Implementation Notes
- Backend: Add recording endpoints (`POST /api/recording/start`, `POST /api/recording/stop`)
- Frontend: Add recording controls to dashboard
- Storage: Save to `recordings/YYYY-MM-DD_HH-MM-SS/` directory
- Gamepad events logged with timestamps for synchronized playback

---

## 11. Appendices

### A. Robot Bridge API Spec (Detailed)

```python
# POST /chassis/move
Request: {"x_speed": 0.3, "y_speed": 0.0, "rotate_speed": 0}
Response: {"status": "ok"} | {"error": "not_connected"}

# POST /gimbal/move  
Request: {"yaw": 45, "pitch": -10, "speed": 90}
Response: {"status": "ok"}

# GET /video/stream
Response: MJPEG stream (multipart/x-mixed-replace)
```

### B. Gamepad Dead Zones

```typescript
const DEAD_ZONE = 0.15;  // Ignore inputs below this threshold

function applyDeadZone(value: number): number {
  if (Math.abs(value) < DEAD_ZONE) return 0;
  // Normalize remaining range to 0-1
  return (value - Math.sign(value) * DEAD_ZONE) / (1 - DEAD_ZONE);
}
```

### C. Command Rate Limiting

```python
# In backend safety layer
COMMANDS_PER_SECOND = 60
MIN_COMMAND_INTERVAL = 1 / COMMANDS_PER_SECOND  # ~16.67ms

async def validate_rate(client_id: str) -> bool:
    last = get_last_command_time(client_id)
    if time.now() - last < MIN_COMMAND_INTERVAL:
        return False
    update_last_command_time(client_id)
    return True
```

---

**End of PRD**

This document is ready for implementation. Next step: Run planning command to create detailed implementation tasks.