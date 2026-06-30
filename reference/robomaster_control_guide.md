# RoboMaster S1 Control Tool Guide

**Load this when:** Creating a Python tool to control the DJI RoboMaster S1 robot via the `robomaster` SDK.

---

## Overall Pattern

```
Install SDK → Connect to Robot → Send Commands → Handle Responses
```

The RoboMaster S1 is controlled via WiFi using the official `robomaster` Python SDK (Python 3.8 only). Commands are sent over TCP (port 40923) in Router Connection Mode.

---

## Step 1: Install the SDK

```bash
pip install robomaster
```

**Key Rules:**
- Requires **Python 3.8** (SDK limitation)
- Robot must be in **Router Connection Mode**
- Robot and computer must share same WiFi network

---

## Step 2: Connect to Robot

```python
from robomaster import robot, rm_define

class RoboMasterController:
    def __init__(self):
        self.robot = None
        self.chassis = None
        self.gimbal = None
        self.led = None

    def connect(self, conn_type: str = "sta") -> bool:
        """Connect using 'sta' (router) or 'ap' (direct) mode."""
        try:
            self.robot = robot.Robot()
            self.robot.initialize(conn_type=conn_type)
            self.chassis = self.robot.chassis
            self.gimbal = self.robot.gimbal
            self.led = self.robot.led
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def disconnect(self):
        if self.robot:
            self.robot.close()

# Usage
ctrl = RoboMasterController()
if ctrl.connect("sta"):
    # Execute commands...
    ctrl.disconnect()
```

**Key Rules:**
- Call `initialize()` before accessing components
- Store component references for reuse
- Call `close()` on disconnect

---

## Step 3: Control Chassis Movement

```python
# Set safety speed limits (AI max: 0.5 m/s)
ctrl.chassis.set_trans_speed(0.5)
ctrl.chassis.set_rotate_speed(30)

# Move by distance (blocking)
ctrl.chassis.move(x=1, y=0).wait_for_completed()  # 1m forward

# Translate at angle for duration (0=forward, 90=right, -90=left)
ctrl.chassis.move(degree=0).exec_time(2.0)

# Rotate in place
ctrl.chassis.rotate(rm_define.clockwise).exec_time(1.0)

# Emergency stop
ctrl.chassis.stop()
```

**Key Rules:**
- `move(x, y)`: x=forward, y=right (robot-relative)
- `wait_for_completed()` blocks until done
- Always call `stop()` to halt movements

---

## Step 4: Control Gimbal

```python
# Set rotation speed (0-540 deg/s)
ctrl.gimbal.set_rotate_speed(100)

# Move to absolute position
ctrl.gimbal.moveto(
    yaw=90, pitch=0,
    yaw_speed=100, pitch_speed=100
)  # yaw: -250 to +250, pitch: -20 to +35

# Recenter to (0, 0)
ctrl.gimbal.recenter()
```

**Key Rules:**
- Yaw range: -250° to +250° (0 = centered)
- Pitch range: -20° to +35° (negative = down)
- Use lower speeds (50-100) for precise aiming

---

## Step 5: Control LEDs

```python
# Chassis LEDs (RGB 0-255)
ctrl.led.set_bottom_led(
    rm_define.armor_bottom_all,
    r=0, g=255, b=0,
    effect=rm_define.effect_always_on  # always_on, breath, flash
)

# Gimbal LEDs
ctrl.led.set_top_led(
    rm_define.armor_top_all,
    r=255, g=0, b=0,
    effect=rm_define.effect_flash
)

# Turn off all LEDs
ctrl.led.turn_off(rm_define.armor_all)
```

**Key Rules:**
- Chassis: `armor_bottom_*` | Gimbal: `armor_top_*`
- Effects: `always_on`, `always_off`, `breath`, `flash`, `marquee`

---

## Step 6: Demo Program

```python
def demo_square_pattern():
    """Connect, move in square, flash LEDs."""
    ctrl = RoboMasterController()
    if not ctrl.connect("sta"):
        return
    try:
        ctrl.chassis.set_trans_speed(0.3)
        ctrl.led.set_bottom_led(
            rm_define.armor_bottom_all, 0, 255, 0,
            rm_define.effect_always_on
        )
        for _ in range(4):
            ctrl.chassis.move(x=0.5, y=0).wait_for_completed()
            ctrl.chassis.rotate(rm_define.clockwise).exec_time(0.5)
        ctrl.led.set_bottom_led(
            rm_define.armor_bottom_all, 0, 0, 255,
            rm_define.effect_breath
        )
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ctrl.led.turn_off(rm_define.armor_all)
        ctrl.disconnect()

if __name__ == "__main__":
    demo_square_pattern()
```

**Key Rules:**
- Wrap in try/except/finally
- Use finally for guaranteed cleanup
- Test in safe environment first

---

## Quick Checklist

- [ ] Install SDK: `pip install robomaster`
- [ ] Use Python 3.8 (required by SDK)
- [ ] Robot in Router Connection Mode
- [ ] Computer and robot on same network
- [ ] Set safety speed: translation ≤0.5 m/s
- [ ] Handle connection errors in try/except
- [ ] Use `wait_for_completed()` for blocking moves
- [ ] Call `chassis.stop()` to halt movement
- [ ] Respect gimbal ranges: yaw [-250, 250], pitch [-20, 35]
- [ ] Cleanup: `led.turn_off()`, `robot.close()`
- [ ] Test in open area with safety distance
