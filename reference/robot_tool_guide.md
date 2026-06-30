# RoboMaster S1 Robot Control Tool Guide

**Load this when:** Creating Pydantic AI tools to control the DJI RoboMaster S1 robot.

---

## Overall Pattern

Robot control tools follow a **safety-first adapter pattern**:

```
Pydantic AI Tool → Safety Validation → SDK Adapter → RoboMaster Robot
```

The SDK (`pip install robomaster`) provides direct control via WiFi connection. Tools must validate safety constraints before execution.

---

## Step 1: Install SDK and Setup Connection

```bash
pip install robomaster
```

```python
from robomaster import robot, conn
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class RobotController:
    """Adapter for RoboMaster S1 robot connection."""

    def __init__(self):
        self.robot: robot.Robot | None = None
        self.is_connected = False

    async def connect(self, ip: str = "192.168.2.1", port: int = 40923) -> bool:
        """Connect to robot via direct connection mode."""
        try:
            self.robot = robot.Robot()
            self.robot.initialize(conn_type="sta", sn="")  # Router mode
            self.is_connected = True
            logger.info("robot_connected", ip=ip)
            return True
        except Exception as e:
            logger.error("robot_connection_failed", error=str(e))
            return False

    def disconnect(self):
        if self.robot:
            self.robot.close()
            self.is_connected = False
```

**Key Rules:**
- Robot must be in **Router Connection Mode** (not direct connection)
- Connection is TCP-based via port 40923
- Always wrap SDK calls in try/except for connection failures
- Log all connection attempts with IP/result

---

## Step 2: Create Safety Validation Layer

```python
from pydantic import BaseModel, Field

class SafetyLimits:
    """Safety constraints for robot operations."""
    MAX_SPEED = 0.5  # m/s for AI-controlled ops
    MAX_DISTANCE = 5000  # mm per command
    MAX_ROTATION_SPEED = 300  # deg/s

class MoveCommand(BaseModel):
    """Validated move command."""
    distance_mm: int = Field(..., ge=0, le=5000)
    speed: float = Field(..., ge=0.0, le=0.5)

    def validate_safety(self) -> tuple[bool, str]:
        """Returns (is_safe, reason_if_unsafe)."""
        if self.speed > SafetyLimits.MAX_SPEED:
            return False, f"Speed {self.speed} exceeds max {SafetyLimits.MAX_SPEED}"
        return True, ""
```

**Key Rules:**
- Maximum AI-controlled speed: **0.5 m/s** (50% of max)
- Validate all parameters before SDK calls
- Return descriptive error messages for rejections
- Never skip safety checks for "quick tests"

---

## Step 3: Implement Movement Tools

```python
from pydantic_ai import Agent, RunContext
from pydantic import Field

@robot_agent.tool
async def move_forward(
    ctx: RunContext[RobotDependencies],
    distance_mm: int = Field(..., ge=0, le=5000, description="Distance in mm"),
    speed: float = Field(..., ge=0.0, le=0.5, description="Speed 0-0.5 m/s"),
) -> str:
    """Move the chassis forward by a specified distance.

    Use this when you need to:
    - Navigate to a target position
    - Move the robot in a straight line forward
    - Adjust position relative to an object ahead

    Do NOT use this for:
    - Rotating in place (use rotate_chassis instead)
    - Emergency stops (use emergency_stop instead)
    - Moving backward (use move_backward instead)

    Args:
        distance_mm: Distance to move in millimeters (0-5000)
        speed: Movement speed 0.0-0.5 m/s (safety limit for AI ops)

    Returns:
        Status message with final position or error
    """
    cmd = MoveCommand(distance_mm=distance_mm, speed=speed)

    # Safety validation
    is_safe, reason = cmd.validate_safety()
    if not is_safe:
        return f"Move rejected: {reason}"

    # Execute via SDK
    try:
        chassis = ctx.deps.robot.chassis
        duration = distance_mm / 1000 / speed  # Calculate time needed
        chassis.move(x=speed, y=0, z=0).exec(duration)
        return f"Moved forward {distance_mm}mm at {speed}m/s"
    except Exception as e:
        logger.error("move_failed", error=str(e))
        return f"Move failed: {str(e)}"
```

**Key Rules:**
- Tool docstrings must include "Use this when", "Do NOT use", and "Args" with ranges
- Validate through safety layer before SDK execution
- Wrap SDK calls in try/except for connection errors
- Return descriptive status messages for agent reasoning

---

## Step 4: Implement Gimbal Control Tools

```python
@robot_agent.tool
async def rotate_gimbal(
    ctx: RunContext[RobotDependencies],
    yaw: int = Field(..., ge=-250, le=250, description="Yaw angle -250 to +250"),
    pitch: int = Field(..., ge=-20, le=35, description="Pitch angle -20 to +35"),
    speed: int = Field(default=100, ge=0, le=540, description="Rotation speed deg/s"),
) -> str:
    """Rotate the gimbal to a specific yaw and pitch angle.

    Use this when you need to:
    - Aim the camera at a target
    - Scan an area with the gimbal
    - Position the blaster for firing

    Do NOT use this for:
    - Continuous rotation (use start_gimbal_rotation instead)
    - Recentering (use recenter_gimbal instead)

    Args:
        yaw: Horizontal angle -250° to +250° (0=center)
        pitch: Vertical angle -20° to +35° (0=level)
        speed: Rotation speed 0-540°/s (lower for precise aiming)
    """
    try:
        gimbal = ctx.deps.robot.gimbal
        gimbal.moveto(yaw=yaw, pitch=pitch, yaw_speed=speed, pitch_speed=speed)
        return f"Gimbal rotated to yaw={yaw}°, pitch={pitch}°"
    except Exception as e:
        return f"Gimbal rotation failed: {str(e)}"
```

**Key Rules:**
- Gimbal yaw range: -250° to +250° (0 is centered)
- Gimbal pitch range: -20° to +35° (negative is down)
- Always specify rotation speed (lower for precision)
- Gimbal controls camera and blaster aim

---

## Step 5: Implement LED and Effect Tools

```python
@robot_agent.tool
async def set_led_color(
    ctx: RunContext[RobotDependencies],
    component: str = Field(..., pattern="^(chassis|gimbal)$"),
    r: int = Field(..., ge=0, le=255, description="Red 0-255"),
    g: int = Field(..., ge=0, le=255, description="Green 0-255"),
    b: int = Field(..., ge=0, le=255, description="Blue 0-255"),
    effect: str = Field(default="solid", pattern="^(solid|breath|flash|off)$"),
) -> str:
    """Set LED colors and effects on chassis or gimbal.

    Use this when you need to:
    - Indicate robot status (green=ready, red=error, blue=working)
    - Create visual feedback for actions
    - Signal state changes to observers

    Do NOT use this for:
    - Controlling movement (use move/rotate tools instead)

    Args:
        component: "chassis" or "gimbal"
        r,g,b: RGB color values 0-255
        effect: "solid", "breath", "flash", or "off"
    """
    try:
        led = ctx.deps.robot.led
        if component == "chassis":
            led.set_mled_bright(r, g, b)
        else:
            led.set_gimbal_led(r, g, b, effect)
        return f"Set {component} LED to RGB({r},{g},{b}) with {effect} effect"
    except Exception as e:
        return f"LED control failed: {str(e)}"
```

**Key Rules:**
- Chassis has bottom LEDs, gimbal has top LEDs
- Effects: solid, breath (pulse), flash, off
- Use colors for status indication consistently

---

## Step 6: Create Agent Dependencies

```python
from dataclasses import dataclass
from robomaster import robot

@dataclass
class RobotDependencies:
    """Dependencies passed to agent tools."""
    robot: robot.Robot
    safety_monitor: SafetyMonitor
    logger: Logger

# Initialize and run agent
async def run_robot_agent(user_prompt: str) -> str:
    controller = RobotController()
    await controller.connect()

    deps = RobotDependencies(
        robot=controller.robot,
        safety_monitor=SafetyMonitor(),
        logger=get_logger(__name__),
    )

    result = await robot_agent.run(user_prompt, deps=deps)
    return result.output
```

**Key Rules:**
- Dependencies must be dataclass or similar
- Pass robot instance, safety monitor, and logger
- Initialize connection before creating deps
- Clean up (disconnect) after agent run

---

## Quick Checklist

- [ ] Install `robomaster` SDK: `pip install robomaster`
- [ ] Create `RobotController` class for connection management
- [ ] Implement safety validation layer with `MAX_SPEED = 0.5`
- [ ] Create Pydantic AI tools with proper agent-optimized docstrings
- [ ] Include "Use this when" and "Do NOT use" in tool docstrings
- [ ] Validate parameters before SDK calls
- [ ] Wrap SDK calls in try/except for connection errors
- [ ] Return descriptive status strings for agent reasoning
- [ ] Create `RobotDependencies` dataclass with robot + safety + logger
- [ ] Test with robot in safe environment before production use
