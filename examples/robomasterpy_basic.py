#!/usr/bin/env python3
"""
RoboMasterPy Basic Example - Simple connection and movement test.

This uses the simpler SDK approach (not the full framework).
For the S1 rooted robot.
"""

import sys
import time
import robomasterpy as rm

# Configuration - change based on your connection mode
# USB Mode (wired): ip = "192.168.42.2"
# Direct WiFi Mode: ip = "192.168.2.1"
# Router Mode: ip = "" (auto-detect via broadcast)
ROBOT_IP = "192.168.42.2"  # Change this based on your setup
TIMEOUT = 30  # seconds


def test_connection():
    """Test basic connection to RoboMaster."""
    print(f"Connecting to RoboMaster at {ROBOT_IP or '(auto-detect)'}...")

    try:
        # Create Commander - connects immediately
        cmd = rm.Commander(ip=ROBOT_IP, timeout=TIMEOUT)
        print("✓ Connected successfully!")

        # Get basic info
        print(f"\n--- Robot Info ---")
        print(f"IP: {cmd.get_ip()}")
        print(f"Version: {cmd.version()}")
        print(f"Mode: {cmd.get_robot_mode()}")

        battery = cmd.get_chassis_status()
        print(f"Status: {battery}")

        return cmd

    except Exception as e:
        print(f"✗ Connection failed: {e}")
        sys.exit(1)


def test_movement(cmd):
    """Test basic chassis movement."""
    print(f"\n--- Testing Movement ---")
    print("Make sure robot has space to move!")
    time.sleep(2)

    # Set robot mode to chassis lead (chassis controls gimbal)
    print("Setting mode to chassis_lead...")
    cmd.robot_mode(rm.MODE_CHASSIS_LEAD)
    time.sleep(0.5)

    # Test 1: Move forward slowly
    print("Moving forward (0.2 m/s for 1 second)...")
    cmd.chassis_speed(x=0.2, y=0, z=0)
    time.sleep(1)

    # Stop
    print("Stopping...")
    cmd.chassis_speed(x=0, y=0, z=0)
    time.sleep(0.5)

    # Test 2: Rotate
    print("Rotating (30 deg/s for 1 second)...")
    cmd.chassis_speed(x=0, y=0, z=30)
    time.sleep(1)

    # Stop
    print("Stopping...")
    cmd.chassis_speed(x=0, y=0, z=0)
    time.sleep(0.5)

    # Test 3: Distance-based movement
    print("Moving forward 0.3m...")
    cmd.chassis_move(x=0.3, speed_xy=0.3)
    time.sleep(2)  # Wait for movement to complete

    print("✓ Movement tests complete!")


def test_gimbal(cmd):
    """Test gimbal movement."""
    print(f"\n--- Testing Gimbal ---")

    # Recenter first
    print("Recentering gimbal...")
    cmd.gimbal_recenter()
    time.sleep(1)

    # Move gimbal
    print("Moving gimbal up 20 degrees...")
    cmd.gimbal_move(pitch=20, pitch_speed=30)
    time.sleep(1)

    print("Moving gimbal down 20 degrees...")
    cmd.gimbal_move(pitch=-20, pitch_speed=30)
    time.sleep(1)

    print("Moving gimbal right 45 degrees...")
    cmd.gimbal_move(yaw=45, yaw_speed=60)
    time.sleep(1)

    print("Recentering...")
    cmd.gimbal_recenter()
    time.sleep(1)

    print("✓ Gimbal tests complete!")


def test_leds(cmd):
    """Test LED control."""
    print(f"\n--- Testing LEDs ---")

    # Red
    print("LEDs: Red")
    cmd.led_control(comp=rm.LED_ALL, effect=rm.LED_EFFECT_ON, r=255, g=0, b=0)
    time.sleep(1)

    # Green
    print("LEDs: Green")
    cmd.led_control(comp=rm.LED_ALL, effect=rm.LED_EFFECT_ON, r=0, g=255, b=0)
    time.sleep(1)

    # Blue
    print("LEDs: Blue")
    cmd.led_control(comp=rm.LED_ALL, effect=rm.LED_EFFECT_ON, r=0, g=0, b=255)
    time.sleep(1)

    # Off
    print("LEDs: Off")
    cmd.led_control(comp=rm.LED_ALL, effect=rm.LED_EFFECT_OFF, r=0, g=0, b=0)

    print("✓ LED tests complete!")


def test_sensors(cmd):
    """Test sensor queries."""
    print(f"\n--- Testing Sensors ---")

    # Chassis attitude
    attitude = cmd.get_chassis_attitude()
    print(
        f"Chassis Attitude: pitch={attitude.pitch:.2f}°, roll={attitude.roll:.2f}°, yaw={attitude.yaw:.2f}°"
    )

    # Chassis position
    position = cmd.get_chassis_position()
    print(
        f"Chassis Position: x={position.x:.2f}m, y={position.y:.2f}m, z={position.z:.2f}°"
    )

    # Gimbal attitude
    gimbal = cmd.get_gimbal_attitude()
    print(f"Gimbal Attitude: pitch={gimbal.pitch:.2f}°, yaw={gimbal.yaw:.2f}°")

    print("✓ Sensor tests complete!")


def main():
    """Main test sequence."""
    print("=" * 50)
    print("RoboMasterPy Basic Test")
    print("=" * 50)
    print("\n⚠️  SAFETY: Ensure robot has clearance to move!")
    print("Starting in 3 seconds...")
    time.sleep(3)

    # Connect
    cmd = test_connection()

    try:
        # Run tests
        test_sensors(cmd)
        test_leds(cmd)
        test_gimbal(cmd)
        test_movement(cmd)

        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("=" * 50)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Cleanup
        print("\nCleaning up...")
        cmd.chassis_speed(x=0, y=0, z=0)  # Ensure stopped
        cmd.gimbal_recenter()
        cmd.close()
        print("Disconnected.")


if __name__ == "__main__":
    main()
