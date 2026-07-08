# RoboMasterPy Guide

**Use this when:** Controlling DJI RoboMaster S1/EP with the RoboMasterPy SDK.

---

## Quick Start

```bash
pip install robomasterpy opencv-contrib-python
```

```python
import robomasterpy as rm

# Connect (auto-detects IP in router mode, or specify IP)
cmd = rm.Commander(ip="192.168.42.2")  # USB mode

# Basic movement
cmd.chassis_speed(x=0.3)  # Move forward at 0.3 m/s
cmd.chassis_speed(x=0)    # Stop

# Cleanup
cmd.close()
```

---

## Connection Modes

| Mode | IP Address | Use Case |
|------|------------|----------|
| USB | `192.168.42.2` | Wired connection (most reliable) |
| Direct WiFi | `192.168.2.1` | Connect to robot's WiFi |
| Router | `""` (auto) | Robot on same network |

**Important:**
- Robot must be in SDK mode (enabled in RoboMaster App)
- S1 requires rooted firmware for external SDK access
- EP works out of the box

---

## Core API

### Commander Creation

```python
import robomasterpy as rm

# Auto-detect IP (router mode only)
cmd = rm.Commander()

# Explicit IP (recommended)
cmd = rm.Commander(ip="192.168.42.2", timeout=30)

# Always close when done
cmd.close()
```

### Robot Modes

```python
cmd.robot_mode(rm.MODE_CHASSIS_LEAD)  # Chassis direction = forward
cmd.robot_mode(rm.MODE_GIMBAL_LEAD)   # Gimbal direction = forward
cmd.robot_mode(rm.MODE_FREE)          # Independent control
```

### Chassis Movement

```python
# Speed control (continuous)
cmd.chassis_speed(x=0.3, y=0, z=0)   # Forward 0.3 m/s
cmd.chassis_speed(x=0, y=0, z=30)    # Rotate 30 deg/s
cmd.chassis_speed(x=0, y=0, z=0)     # Stop

# Position control (moves then stops)
cmd.chassis_move(x=1.0, speed_xy=0.5)      # Forward 1m at 0.5 m/s
cmd.chassis_move(z=90, speed_z=30)         # Rotate 90° at 30°/s
cmd.chassis_move(x=0.5, y=0.3, z=45)       # Combined movement

# Individual wheel control (RPM)
cmd.chassis_wheel(w1=100, w2=100, w3=100, w4=100)  # All forward
cmd.chassis_wheel(w1=0, w2=0, w3=0, w4=0)          # Stop
```

**Safety Limits (AI):**
- Max speed: 0.5 m/s
- Max rotation: 100 deg/s

### Gimbal Control

```python
# Recenter
cmd.gimbal_recenter()

# Relative movement (from current position)
cmd.gimbal_move(pitch=20, yaw=45)           # Up 20°, right 45°
cmd.gimbal_move(pitch=-20, yaw=-45)         # Down 20°, left 45°

# Absolute movement (from center)
cmd.gimbal_moveto(pitch=0, yaw=0)           # Center
cmd.gimbal_moveto(pitch=-30, yaw=90)        # Look down and right

# Continuous speed
cmd.gimbal_speed(pitch=30, yaw=0)   # Rotate up at 30°/s
cmd.gimbal_speed(pitch=0, yaw=0)    # Stop
```

**Ranges:**
- Pitch: -55° to 55° (negative = down)
- Yaw: -250° to 250° (0 = center)
- Speed: -450 to 450 °/s

### LED Control

```python
# Components: LED_ALL, LED_TOP_ALL, LED_BOTTOM_ALL, LED_TOP_LEFT, etc.
# Effects: LED_EFFECT_ON, LED_EFFECT_OFF, LED_EFFECT_FLASH, LED_EFFECT_BREATH

# Solid colors
cmd.led_control(comp=rm.LED_ALL, effect=rm.LED_EFFECT_ON, r=255, g=0, b=0)   # Red
cmd.led_control(comp=rm.LED_ALL, effect=rm.LED_EFFECT_ON, r=0, g=255, b=0)   # Green
cmd.led_control(comp=rm.LED_ALL, effect=rm.LED_EFFECT_ON, r=0, g=0, b=255)   # Blue

# Flash effect
cmd.led_control(comp=rm.LED_ALL, effect=rm.LED_EFFECT_FLASH, r=255, g=0, b=0)

# Turn off
cmd.led_control(comp=rm.LED_ALL, effect=rm.LED_EFFECT_OFF, r=0, g=0, b=0)
```

### Blaster

```python
cmd.blaster_fire()        # Fire once
cmd.blaster_fire()        # Fire again

# Note: Safety switch must be disabled in RoboMaster App
```

### Queries

```python
# Robot info
version = cmd.version()              # e.g., "version 00.00.00.60"
mode = cmd.get_robot_mode()          # "chassis_lead", "gimbal_lead", "free"
ip = cmd.get_ip()                    # Current IP

# Chassis
pos = cmd.get_chassis_position()     # x, y, z (m, m, deg)
att = cmd.get_chassis_attitude()     # pitch, roll, yaw (deg)
speed = cmd.get_chassis_speed()      # x, y, z, w1, w2, w3, w4
status = cmd.get_chassis_status()    # Status flags

# Gimbal
gimbal_att = cmd.get_gimbal_attitude()  # pitch, yaw

# Armor
sensitivity = cmd.get_armor_sensitivity()
```

### Video Stream

```python
# Enable stream
cmd.stream(rm.SWITCH_ON)

# Use framework's Vision worker to process frames
# See Framework section below

# Disable stream
cmd.stream(rm.SWITCH_OFF)
```

### Push & Events

```python
# Enable chassis push (1, 5, 10, 20, 30, 50 Hz)
cmd.chassis_push_on(position_freq=5, attitude_freq=5, status_freq=5)
cmd.chassis_push_on(all_freq=10)  # Set all to 10Hz

# Enable gimbal push
cmd.gimbal_push_on(attitude_freq=5)

# Armor events
cmd.armor_sensitivity(5)  # 0-10, higher = more sensitive
cmd.armor_event(rm.ARMOR_HIT, True)  # Enable hit detection

# Sound events
cmd.sound_event(rm.SOUND_APPLAUSE, True)

# Disable
cmd.chassis_push_off(all=True)
cmd.gimbal_push_off()
```

---

## Framework (Advanced)

For complex applications with video processing and event handling:

```python
import multiprocessing as mp
from robomasterpy import CTX
import robomasterpy as rm
from robomasterpy import framework as rmf

def process_frame(frame, logger):
    """Process video frame (OpenCV format)."""
    # Your computer vision code here
    return frame

def handle_control(cmd, queues, logger):
    """Control logic with access to data queues."""
    # Your control logic here
    cmd.chassis_speed(x=0.2)

# Setup
manager = CTX.Manager()
with manager:
    hub = rmf.Hub()
    cmd = rm.Commander(ip="192.168.42.2")
    ip = cmd.get_ip()

    # Enable features
    cmd.robot_mode(rm.MODE_GIMBAL_LEAD)
    cmd.stream(True)
    cmd.chassis_push_on(all_freq=5)

    # Workers
    push_queue = manager.Queue(100)
    hub.worker(rmf.Vision, 'vision', (None, ip, process_frame))
    hub.worker(rmf.PushListener, 'push', (push_queue,))
    hub.worker(rmf.Mind, 'controller', ((push_queue,), ip, handle_control))

    # Run until Ctrl+C
    hub.run()
```

---

## Constants Reference

```python
# Robot Modes
rm.MODE_CHASSIS_LEAD  # Chassis direction is forward
rm.MODE_GIMBAL_LEAD   # Gimbal direction is forward
rm.MODE_FREE          # Independent control

# LED Components
rm.LED_ALL            # All LEDs
rm.LED_TOP_ALL        # All top LEDs
rm.LED_BOTTOM_ALL     # All bottom LEDs
rm.LED_TOP_LEFT       # Top left LED
rm.LED_TOP_RIGHT      # Top right LED
rm.LED_BOTTOM_LEFT    # Bottom left LED
rm.LED_BOTTOM_RIGHT   # Bottom right LED
rm.LED_BOTTOM_FRONT   # Bottom front LEDs
rm.LED_BOTTOM_BACK    # Bottom back LEDs
rm.LED_BOTTOM_REAR    # Bottom rear LEDs

# LED Effects
rm.LED_EFFECT_ON      # Solid
rm.LED_EFFECT_OFF     # Off
rm.LED_EFFECT_FLASH   # Flashing
rm.LED_EFFECT_BREATH  # Breathing/pulsing

# Switches
rm.SWITCH_ON
rm.SWITCH_OFF

# Armor Events
rm.ARMOR_HIT

# Sound Events
rm.SOUND_APPLAUSE
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection timeout | Verify robot IP, ensure SDK mode enabled in app |
| No movement | Check robot mode (chassis_lead vs gimbal_lead) |
| Gimbal not responding | Call `gimbal_resume()` if suspended |
| Commands fail | Verify robot has latest firmware |
| Video not streaming | Check `cmd.stream(rm.SWITCH_ON)` called |

---

## Quick Checklist

- [ ] `pip install robomasterpy opencv-contrib-python`
- [ ] Robot in SDK mode (enabled in RoboMaster App)
- [ ] Correct IP for connection mode (USB: 192.168.42.2, Direct: 192.168.2.1)
- [ ] Robot has space to move
- [ ] Using `cmd.close()` or context managers for cleanup
- [ ] Safety limits enforced (0.5 m/s max for AI)
