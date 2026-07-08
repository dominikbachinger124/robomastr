# RoboMaster S1 Control Guide

**Load this when:** Writing code to command the RoboMaster S1 robot (movement, LEDs, gimbal, blaster).

---

## Overall Pattern

Plaintext TCP protocol over port 40923. Enter SDK mode with `command;`, then send semicolon-terminated text commands. Always use context managers for automatic cleanup.

```
┌─────────────┐     TCP 40923      ┌─────────────┐
│   Python    │ ◄────────────────► │  RoboMaster │
│  Controller │   command;         │     S1      │
│             │   chassis move...  │             │
└─────────────┘                    └─────────────┘
```

---

## Step 1: Establish TCP Connection

Open socket to robot IP (Direct WiFi: `192.168.2.1`, USB: `192.168.42.2`).

```python
import socket

class S1Controller:
    def __init__(self, host: str = "192.168.2.1", port: int = 40923):
        self.host = host
        self.port = port
        self._sock: socket.socket | None = None

    def connect(self) -> bool:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(5)
        self._sock.connect((self.host, self.port))
        
        response = self.send("command")
        return "ok" in response.lower()

    def send(self, cmd: str) -> str:
        self._sock.send(f"{cmd};".encode())
        return self._sock.recv(1024).decode().strip()
```

**Rules:**
- Always verify ping succeeds before connecting: `ping -c 1 192.168.2.1`
- All commands MUST end with semicolon `;`
- Receive buffer size 1024 bytes is sufficient for all responses

---

## Step 2: Implement Movement Controls

Use `chassis speed` for continuous motion, `chassis move` for distance-based.

```python
    def move_speed(self, x: float = 0, y: float = 0, z: float = 0) -> str:
        """Continuous speed control (m/s, deg/s)."""
        return self.send(f"chassis speed x {x} y {y} z {z}")

    def move_distance(self, x: float = 0, y: float = 0, z: float = 0, 
                      vxy: float = 0.5, vz: int = 30) -> str:
        """Relative distance move (meters, degrees)."""
        return self.send(f"chassis move x {x} y {y} z {z} vxy {vxy} vz {vz}")

    def stop(self) -> str:
        """Emergency stop all wheels."""
        return self.send("chassis wheel w1 0 w2 0 w3 0 w4 0")

    # Convenience methods
    def forward(self, speed: float = 0.3) -> str:
        return self.move_speed(x=speed)

    def rotate(self, speed: float = 30) -> str:
        return self.move_speed(z=speed)
```

**Rules:**
- AI safety limit: max speed 0.5 m/s (`x`, `y`), max rotation 100 deg/s (`z`)
- Speed range: -3.5 to 3.5 m/s (chassis), -600 to 600 deg/s (rotation)
- Always call `stop()` before disconnecting
- Distance commands block until complete (use speeds < 0.5 m/s)

---

## Step 3: Control Gimbal and LEDs

Gimbal uses pitch/yaw axes. LEDs use RGB 0-255 with component targeting.

```python
    def gimbal_speed(self, pitch: float = 0, yaw: float = 0) -> str:
        """Gimbal rotation speed (deg/s)."""
        return self.send(f"gimbal speed p {pitch} y {yaw}")

    def gimbal_move(self, pitch: float = 0, yaw: float = 0, 
                    vpg: float = 30, vyg: float = 30) -> str:
        """Relative gimbal position (degrees)."""
        return self.send(f"gimbal move p {pitch} y {yaw} vp {vpg} vy {vyg}")

    def set_led(self, r: int, g: int, b: int, 
                comp: str = "all", effect: str = "on") -> str:
        """Set LED color. comp: all/top_all/bottom_all/bottom_front/etc."""
        return self.send(f"led control comp {comp} r {r} g {g} b {b} {effect}")

    def blaster_fire(self, count: int = 1) -> str:
        """Fire infrared blaster (count: 1-10)."""
        return self.send(f"blaster fire count {count}")
```

**Rules:**
- Gimbal pitch range: -55° to 55°, yaw: continuous 360°
- LED effect: `on`, `off`, `flash`, `breath` (flash/breath need freq param)
- Blaster only fires if safety switch disabled in app
- Gimbal and chassis are independent coordinate systems

---

## Step 4: Query State and Telemetry

Read-only commands end with `?`, return plaintext values.

```python
    def get_version(self) -> str:
        return self.send("version ?")

    def get_battery(self) -> str:
        return self.send("robot battery ?")

    def get_chassis_speed(self) -> str:
        """Returns: vx vy vz vphi"""
        return self.send("chassis speed ?")

    def get_chassis_position(self) -> str:
        """Returns: x y z"""
        return self.send("chassis position ?")

    def get_gimbal_attitude(self) -> str:
        """Returns: pitch yaw roll"""
        return self.send("gimbal attitude ?")
```

**Rules:**
- Query commands don't change state (safe to call anytime)
- Battery returns percentage (0-100) or "charging" status
- Position is relative to last reset/startup (odometry-based)
- Attitude angles are in degrees, -180 to 180

---

## Step 5: Safe Cleanup Pattern

Always exit SDK mode and close socket, even on exceptions.

```python
    def disconnect(self) -> None:
        """Exit SDK mode and close connection."""
        try:
            if self._sock:
                self.stop()  # Emergency stop first
                self.send("quit")  # Exit SDK mode
        except Exception:
            pass  # Ignore errors during cleanup
        finally:
            if self._sock:
                self._sock.close()
                self._sock = None

    # Context manager support
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False
```

**Rules:**
- Send `quit;` to cleanly exit SDK mode (allows app to reconnect)
- Close socket even if `quit` fails (force cleanup)
- Use context manager (`with S1Controller() as s1:`) for safety

---

## Quick Checklist

- [ ] Verify robot IP is reachable: `ping -c 1 192.168.2.1`
- [ ] Connect TCP socket to port 40923
- [ ] Enter SDK mode: send `command;`, expect `ok`
- [ ] Enforce AI speed limit: ≤ 0.5 m/s for all movements
- [ ] Send `stop()` before any direction change or disconnect
- [ ] Use `chassis move` for precise distance, `chassis speed` for continuous
- [ ] Target specific LED components (`bottom_all`, `top_all`) not just `all`
- [ ] Query battery before long operations: `robot battery ?`
- [ ] Always use context manager or try/finally for disconnect
- [ ] Send `quit;` before closing socket to release SDK lock
