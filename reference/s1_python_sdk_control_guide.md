# S1 Python SDK Control Guide

Control the RoboMaster S1 using the high-level Python SDK (`robomaster` library). Use this guide for action-based movement, sensor subscriptions, vision detection, and AI integration.

---

## Overall Pattern

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐
│   Robot()   │────▶│ initialize  │────▶│  Control Modules │
│   Object    │     │  (conn_type) │     │  chassis/gimbal  │
└─────────────┘     └─────────────┘     └─────────────────┘
                                               │
       ┌───────────────────────────────────────┘
       ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Actions    │────▶│   await     │────▶│   cleanup   │
│ (blocking)  │     │  completion │────▶│   close()   │
└─────────────┘     └─────────────┘     └─────────────┘
```

The SDK uses **action-based** movement with async completion tracking. All commands return immediately but execute asynchronously—poll `action.is_completed` or use callbacks.

---

## Step 1: Initialize Robot Connection

```python
import robomaster
from robomaster import robot

# Initialize robot (S1 is already rooted, use 'sta' for network mode)
ep_robot = robot.Robot()
ep_robot.initialize(conn_type='sta')  # or 'ap' for direct WiFi

# Verify connection
print(f"Robot SN: {ep_robot.get_sn()}")
print(f"Version: {ep_robot.get_version()}")
```

**Rules:**
- Always call `initialize()` before any control commands
- Use `conn_type='sta'` for router-connected S1, `'ap'` for direct WiFi
- SDK requires Python 3.6.5+ (bridge uses 3.8)
- Never skip `close()` on shutdown—leaves robot in bad state

---

## Step 2: Control Chassis Movement

```python
ep_chassis = ep_robot.chassis

# Immediate speed control (non-blocking, use timeout for safety)
ep_chassis.drive_speed(x=0.5, y=0.0, z=0.0, timeout=2.0)  # forward 0.5 m/s

# Position-based movement (blocking action)
action = ep_chassis.move(x=1.0, y=0, z=0, xy_speed=0.5)
action.wait_for_completed()  # blocks until done

# Rotate in place
action = ep_chassis.move(x=0, y=0, z=90, z_speed=30)  # 90° clockwise
action.wait_for_completed()

# Direct mecanum wheel control (rpm)
ep_chassis.drive_wheels(w1=100, w2=-100, w3=-100, w4=100)  # strafe right
```

**Limits (enforced by SDK):**
- `drive_speed`: x,y ∈ [-3.5, 3.5] m/s; z ∈ [-600, 600] °/s
- `move`: x,y ∈ [-5, 5] m; z ∈ [-1800, 1800] °; xy_speed ∈ [0.5, 2.0] m/s
- `drive_wheels`: each wheel ∈ [-1000, 1000] rpm

---

## Step 3: Control Gimbal Movement

```python
ep_gimbal = ep_robot.gimbal

# Speed control (continuous)
ep_gimbal.drive_speed(pitch_speed=30, yaw_speed=-30)

# Move relative to current position
action = ep_gimbal.move(pitch=10, yaw=45, pitch_speed=50, yaw_speed=50)
action.wait_for_completed()

# Move to absolute position (from power-on origin)
action = ep_gimbal.moveto(pitch=0, yaw=0, pitch_speed=60, yaw_speed=60)  # recenter
action.wait_for_completed()

# Quick recenter
action = ep_gimbal.recenter(pitch_speed=60, yaw_speed=60)
action.wait_for_completed()
```

**Limits:**
- `move`: pitch ∈ [-55, 55]°, yaw ∈ [-55, 55]°
- `moveto`: pitch ∈ [-25, 30]°, yaw ∈ [-250, 250]°
- Speed: ∈ [0, 540] °/s for both axes

---

## Step 4: Fire Blaster & Control LEDs

```python
ep_blaster = ep_robot.blaster
ep_led = ep_robot.led

# Fire water beads (1-3 burst)
ep_blaster.fire(fire_type=robomaster.blaster.WATER_FIRE, times=1)

# Fire IR (simulated)
ep_blaster.fire(fire_type=robomaster.blaster.INFRARED_FIRE, times=1)

# Set blaster LED
ep_blaster.set_led(brightness=255, effect=robomaster.blaster.LED_ON)

# Armor LED effects
ep_led.set_led(
    comp=robomaster.led.COMP_ALL,  # or COMP_TOP_LEFT, COMP_BOTTOM_ALL, etc.
    r=255, g=0, b=0,               # red
    effect=robomaster.led.EFFECT_BREATH,
    freq=2
)
# Effects: EFFECT_ON, EFFECT_OFF, EFFECT_FLASH, EFFECT_BREATH, EFFECT_SCROLLING
```

**Rules:**
- Water fire: times ∈ [1, 3] per call
- LED brightness: ∈ [0, 255]
- Scroll effect only works on gimbal (top) LEDs

---

## Step 5: Vision Detection

```python
ep_vision = ep_robot.vision

# Define callback for detection
def on_detect_person(person_info):
    for person in person_info:
        x, y, w, h = person  # center x,y and dimensions
        print(f"Person at ({x}, {y}), size {w}x{h}")

# Subscribe to detection
ep_vision.sub_detect_info(
    name="person",           # "person", "gesture", "line", "marker", "robot"
    callback=on_detect_person
)

# For line/marker detection, specify color
ep_vision.sub_detect_info(
    name="marker",
    color="red",             # "red", "green", "blue"
    callback=on_marker_detect
)

# Unsubscribe when done
ep_vision.unsub_detect_info("person")
```

**Detection Types:**
- `person`: Returns [(x, y, w, h), ...]
- `gesture`: Returns [(x, y, w, h, gesture_name), ...]
- `line`: Returns [(x, y, theta, C), ...]  (theta=angle, C=curvature)
- `marker`: Returns [(x, y, w, h, marker_id), ...]
- `robot`: Returns [(x, y, w, h), ...]

---

## Step 6: Subscribe to Sensor Data

```python
# Chassis position (X, Y, Z in meters)
def position_callback(position):
    x, y, z = position
    print(f"Position: x={x:.2f}, y={y:.2f}, z={z:.2f}")

ep_chassis.sub_position(freq=5, callback=position_callback)

# Attitude (yaw, pitch, roll)
def attitude_callback(attitude):
    yaw, pitch, roll = attitude
    print(f"Attitude: yaw={yaw:.1f}°")

ep_chassis.sub_attitude(freq=5, callback=attitude_callback)

# IMU data
def imu_callback(imu):
    acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z = imu
    print(f"Accel: {acc_x}, {acc_y}, {acc_z}")

ep_chassis.sub_imu(freq=10, callback=imu_callback)

# Gimbal angles
def gimbal_callback(gimbal_pos):
    pitch, yaw, pitch_ground, yaw_ground = gimbal_pos
    print(f"Gimbal: pitch={pitch}, yaw={yaw}")

ep_gimbal.sub_angle(freq=5, callback=gimbal_callback)

# Cleanup subscriptions
ep_chassis.unsub_position()
ep_chassis.unsub_attitude()
ep_gimbal.unsub_angle()
```

**Frequency Options:** 1, 5, 10, 20, 50 Hz

---

## Step 7: Cleanup

```python
# Stop all movement
ep_chassis.drive_speed(0, 0, 0)
ep_gimbal.drive_speed(0, 0)

# Unsubscribe all
ep_vision.unsub_detect_info("person")
ep_chassis.unsub_position()

# Close robot connection
ep_robot.close()
```

---

## Quick Checklist

- [ ] Import `robomaster` and create `Robot()` instance
- [ ] Call `initialize(conn_type='sta')` and verify SN/version
- [ ] Use `drive_speed()` for immediate control with timeout
- [ ] Use `move()`/`moveto()` for position-based actions
- [ ] Always `wait_for_completed()` on actions or poll `action.is_completed`
- [ ] Validate speeds: chassis ≤3.5 m/s, gimbal ≤540 °/s
- [ ] Subscribe to position/attitude for feedback loops
- [ ] Set LED effects for status indication
- [ ] Use vision callbacks for autonomous behavior
- [ ] Call `close()` on shutdown to release SDK mode
