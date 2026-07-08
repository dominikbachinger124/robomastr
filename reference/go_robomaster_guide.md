# RoboMaster Modular Control Guide

**Use this when:** Building a modular Python controller following the Go library's architecture (client → modules → commands).

---

## Overall Pattern

Modular architecture with a central Client managing hardware modules. Each module (Chassis, Gimbal, Gun) handles specific robot capabilities through a unified communication layer.

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│   Module     │────▶│   Robot     │
│  (Manager)  │     │ (Chassis/    │     │  Hardware   │
│             │◄────│  Gimbal/Gun) │◄────│             │
└─────────────┘     └──────────────┘     └─────────────┘
```

---

## Step 1: Create Modular Client

```python
from __future__ import annotations
import logging
from typing import Optional
from contextlib import contextmanager


class RoboMasterClient:
    """Central client managing all robot modules."""
    
    def __init__(self, ip: str = "", logger: Optional[logging.Logger] = None):
        self._logger = logger or logging.getLogger(__name__)
        self._ip = ip
        self._started = False
        
        # Initialize modules
        self._connection = ConnectionModule(self._logger, ip)
        self._robot = RobotModule(self._logger, self._connection)
        self._chassis: Optional[ChassisModule] = None
        self._gimbal: Optional[GimbalModule] = None
        self._gun: Optional[GunModule] = None
    
    def start(self) -> None:
        """Start client and all modules."""
        if self._started:
            raise RuntimeError("Client already started")
        
        self._connection.connect()
        self._robot.wait_for_devices(timeout=10)
        
        # Start optional modules
        self._chassis = ChassisModule(self._logger, self._connection, self._robot)
        self._gimbal = GimbalModule(self._logger, self._connection)
        self._gun = GunModule(self._logger, self._connection, self._robot)
        
        self._started = True
        self._logger.info("Client started")
    
    def stop(self) -> None:
        """Stop all modules and cleanup."""
        if not self._started:
            return
        
        if self._gun:
            self._gun.stop()
        if self._gimbal:
            self._gimbal.stop()
        if self._chassis:
            self._chassis.stop()
        
        self._robot.stop()
        self._connection.disconnect()
        self._started = False
    
    def chassis(self) -> ChassisModule:
        if not self._chassis:
            raise RuntimeError("Chassis module not initialized")
        return self._chassis
    
    def gimbal(self) -> GimbalModule:
        if not self._gimbal:
            raise RuntimeError("Gimbal module not initialized")
        return self._gimbal
    
    def gun(self) -> GunModule:
        if not self._gun:
            raise RuntimeError("Gun module not initialized")
        return self._gun
```

**Rules:**
- Client is the single entry point for all robot operations
- Modules are lazily initialized in `start()`
- Always call `stop()` for graceful shutdown
- Use typed getters (`chassis()`, `gimbal()`) to access modules

---

## Step 2: Implement Chassis Module

```python
import time
from enum import IntEnum


class ChassisMode(IntEnum):
    YAW_FOLLOW = 0
    SPEED_MODE = 1


class ChassisModule:
    """Controls robot chassis movement."""
    
    MAX_SPEED_MPS = 3.5
    MAX_ROTATION_DPS = 360
    AI_MAX_SPEED = 0.5
    
    def __init__(self, logger, connection, robot):
        self._logger = logger
        self._conn = connection
        self._robot = robot
    
    def set_mode(self, mode: ChassisMode) -> None:
        """Set chassis control mode."""
        if not isinstance(mode, ChassisMode):
            raise ValueError(f"Invalid mode: {mode}")
        
        self._conn.send_command(f"robot mode {mode.name.lower()}")
        time.sleep(0.333)  # Mode change settling time
        self.stop_movement(mode)
    
    def set_speed(self, x: float, y: float, z: float, 
                  mode: ChassisMode = ChassisMode.YAW_FOLLOW) -> None:
        """Set chassis speed (m/s for x/y, deg/s for z)."""
        # Validate limits
        if abs(x) > self.MAX_SPEED_MPS or abs(y) > self.MAX_SPEED_MPS:
            raise ValueError(f"Speed x/y must be <= {self.MAX_SPEED_MPS}")
        if abs(z) > self.MAX_ROTATION_DPS:
            raise ValueError(f"Rotation z must be <= {self.MAX_ROTATION_DPS}")
        
        self._conn.send_command(f"chassis speed x {x} y {y} z {z}")
    
    def set_position(self, x: float = 0, y: float = 0, z: float = 0,
                     speed_xy: float = 0.5, speed_z: float = 30) -> None:
        """Move to relative position (meters for x/y, degrees for z)."""
        cmd = f"chassis move x {x} y {y} z {z}"
        if speed_xy:
            cmd += f" vxy {speed_xy}"
        if speed_z:
            cmd += f" vz {speed_z}"
        self._conn.send_command(cmd)
    
    def stop_movement(self, mode: ChassisMode = ChassisMode.YAW_FOLLOW) -> None:
        """Stop all chassis movement."""
        self.set_speed(0, 0, 0, mode)
    
    def stop(self) -> None:
        """Cleanup module."""
        self.stop_movement()
```

**Rules:**
- Validate all speed inputs against MAX limits
- Always call `stop_movement()` after mode changes
- Use `set_speed()` for continuous, `set_position()` for relative moves
- Apply AI_MAX_SPEED (0.5 m/s) for autonomous operations

---

## Step 3: Implement Gimbal Module

```python
from enum import IntEnum


class GimbalAxis(IntEnum):
    PITCH = 0
    YAW = 1


class GimbalModule:
    """Controls camera gimbal movement."""
    
    MAX_ROTATION_SPEED = 360  # deg/s
    MAX_PITCH_ANGLE = 60
    MIN_PITCH_ANGLE = -60
    
    def __init__(self, logger, connection):
        self._logger = logger
        self._conn = connection
    
    def set_rotation_speed(self, pitch: int, yaw: int) -> None:
        """Set continuous rotation speed (deg/s)."""
        if abs(pitch) > self.MAX_ROTATION_SPEED:
            raise ValueError(f"Pitch speed must be <= {self.MAX_ROTATION_SPEED}")
        if abs(yaw) > self.MAX_ROTATION_SPEED:
            raise ValueError(f"Yaw speed must be <= {self.MAX_ROTATION_SPEED}")
        
        self._conn.send_command(f"gimbal speed p {pitch} y {yaw}")
    
    def set_relative_rotation(self, angle: int, axis: GimbalAxis,
                              duration_ms: int = 1000) -> None:
        """Rotate relative to current position."""
        if duration_ms > 10000:
            raise ValueError("Duration max is 10000ms")
        
        if axis == GimbalAxis.PITCH:
            if not (-60 <= angle <= 60):
                raise ValueError("Pitch angle must be between -60 and 60")
            self._conn.send_command(
                f"gimbal move p {angle} vp {duration_ms // 10}"
            )
        else:
            self._conn.send_command(
                f"gimbal move y {angle} vy {duration_ms // 10}"
            )
    
    def set_absolute_rotation(self, pitch: int = 0, yaw: int = 0,
                              duration_ms: int = 1000) -> None:
        """Rotate to absolute position from center."""
        if not (-25 <= pitch <= 35):
            raise ValueError("Absolute pitch must be between -25 and 35")
        
        self._conn.send_command(
            f"gimbal moveto p {pitch} y {yaw} vp {duration_ms // 10} vy {duration_ms // 10}"
        )
    
    def stop_rotation(self) -> None:
        """Stop gimbal movement."""
        self.set_rotation_speed(0, 0)
    
    def reset_position(self) -> None:
        """Recenter gimbal."""
        self._conn.send_command("gimbal recenter")
    
    def stop(self) -> None:
        """Cleanup module."""
        self.stop_rotation()
```

**Rules:**
- Pitch range: -60° to +60° relative, -25° to +35° absolute
- Yaw range: continuous 360°
- Always call `stop_rotation()` before changing modes
- Use `reset_position()` on initialization for known state

---

## Step 4: Implement Gun Module

```python
class GunModule:
    """Controls blaster/gun."""
    
    def __init__(self, logger, connection, robot):
        self._logger = logger
        self._conn = connection
        self._robot = robot
    
    def fire(self, count: int = 1) -> None:
        """Fire blaster (count: 1-10)."""
        if not 1 <= count <= 10:
            raise ValueError("Count must be between 1 and 10")
        
        if count == 1:
            self._conn.send_command("blaster fire")
        else:
            self._conn.send_command(f"blaster fire count {count}")
    
    def stop(self) -> None:
        """Cleanup module (nothing required)."""
        pass
```

**Rules:**
- Gun is optional module (may not connect on all robots)
- Verify safety switch is disabled in RoboMaster App
- Max 10 shots per command

---

## Quick Checklist

- [ ] Create `RoboMasterClient` with IP and logger
- [ ] Call `client.start()` to initialize all modules
- [ ] Access modules via `client.chassis()`, `client.gimbal()`, `client.gun()`
- [ ] Set chassis mode before movement (`YAW_FOLLOW` or `SPEED_MODE`)
- [ ] Validate speed limits (3.5 m/s max, 0.5 m/s for AI)
- [ ] Call `reset_position()` on gimbal before operations
- [ ] Use `stop_rotation()` and `stop_movement()` before mode changes
- [ ] Call `client.stop()` for graceful shutdown
- [ ] Handle module initialization errors (Gun is optional)
