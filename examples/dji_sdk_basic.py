#!/usr/bin/env python3
"""
DJI RoboMaster SDK Basic Test
Based on the official DJI robomaster SDK pattern from move2.py

Connection modes:
- "ap": Direct WiFi (robot as AP)
- "sta": Station mode (robot connects to router)
- "rndis": USB connection
"""

import time
from robomaster import robot


def test_basic_movement(conn_type: str = "ap"):
    """
    Test basic chassis movements using official DJI SDK.

    Args:
        conn_type: Connection type - "ap" (Direct WiFi), "sta" (Router), "rndis" (USB)
    """
    print(f"Connecting to robot via {conn_type} mode...")

    # Initialize robot
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type=conn_type)
    print("✓ Connected!")

    # Get chassis module
    ep_chassis = ep_robot.chassis

    try:
        print("\n--- Testing Movements ---")

        # Forward 0.5m
        print("Moving forward 0.5m...")
        ep_chassis.move(x=0.5, y=0, z=0, xy_speed=0.5).wait_for_completed()
        time.sleep(0.5)

        # Backward 0.5m
        print("Moving backward 0.5m...")
        ep_chassis.move(x=-0.5, y=0, z=0, xy_speed=0.5).wait_for_completed()
        time.sleep(0.5)

        # Left 0.5m
        print("Moving left 0.5m...")
        ep_chassis.move(x=0, y=-0.5, z=0, xy_speed=0.5).wait_for_completed()
        time.sleep(0.5)

        # Right 0.5m
        print("Moving right 0.5m...")
        ep_chassis.move(x=0, y=0.5, z=0, xy_speed=0.5).wait_for_completed()
        time.sleep(0.5)

        # Rotate left 90 degrees
        print("Rotating left 90°...")
        ep_chassis.move(x=0, y=0, z=90, z_speed=45).wait_for_completed()
        time.sleep(0.5)

        # Rotate right 90 degrees
        print("Rotating right 90°...")
        ep_chassis.move(x=0, y=0, z=-90, z_speed=45).wait_for_completed()
        time.sleep(0.5)

        print("\n✓ All movements completed!")

    except Exception as e:
        print(f"\n✗ Error during movement: {e}")

    finally:
        # Always close connection
        print("\nClosing connection...")
        ep_robot.close()
        print("Disconnected.")


def test_gimbal(conn_type: str = "ap"):
    """Test gimbal movements."""
    print(f"Connecting to robot via {conn_type} mode...")

    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type=conn_type)
    print("✓ Connected!")

    try:
        ep_gimbal = ep_robot.gimbal

        print("\n--- Testing Gimbal ---")

        # Recenter
        print("Recentering gimbal...")
        ep_gimbal.moveto(
            pitch=0, yaw=0, pitch_speed=100, yaw_speed=100
        ).wait_for_completed()
        time.sleep(0.5)

        # Look up
        print("Looking up...")
        ep_gimbal.moveto(
            pitch=20, yaw=0, pitch_speed=100, yaw_speed=100
        ).wait_for_completed()
        time.sleep(0.5)

        # Look down
        print("Looking down...")
        ep_gimbal.moveto(
            pitch=-20, yaw=0, pitch_speed=100, yaw_speed=100
        ).wait_for_completed()
        time.sleep(0.5)

        # Look left
        print("Looking left...")
        ep_gimbal.moveto(
            pitch=0, yaw=-45, pitch_speed=100, yaw_speed=100
        ).wait_for_completed()
        time.sleep(0.5)

        # Look right
        print("Looking right...")
        ep_gimbal.moveto(
            pitch=0, yaw=45, pitch_speed=100, yaw_speed=100
        ).wait_for_completed()
        time.sleep(0.5)

        # Back to center
        print("Back to center...")
        ep_gimbal.moveto(
            pitch=0, yaw=0, pitch_speed=100, yaw_speed=100
        ).wait_for_completed()

        print("\n✓ Gimbal tests completed!")

    except Exception as e:
        print(f"\n✗ Error: {e}")

    finally:
        print("\nClosing connection...")
        ep_robot.close()
        print("Disconnected.")


def test_leds(conn_type: str = "ap"):
    """Test LED control."""
    print(f"Connecting to robot via {conn_type} mode...")

    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type=conn_type)
    print("✓ Connected!")

    try:
        ep_led = ep_robot.led

        print("\n--- Testing LEDs ---")

        # Set gimbal LEDs to red
        print("LEDs: Red")
        ep_led.set_gimbal_led(r=255, g=0, b=0, effect=ep_led.EFFECT_ON)
        time.sleep(1)

        # Set gimbal LEDs to green
        print("LEDs: Green")
        ep_led.set_gimbal_led(r=0, g=255, b=0, effect=ep_led.EFFECT_ON)
        time.sleep(1)

        # Set gimbal LEDs to blue
        print("LEDs: Blue")
        ep_led.set_gimbal_led(r=0, g=0, b=255, effect=ep_led.EFFECT_ON)
        time.sleep(1)

        # Flash effect
        print("LEDs: Flash yellow")
        ep_led.set_gimbal_led(r=255, g=255, b=0, effect=ep_led.EFFECT_FLASH)
        time.sleep(2)

        # Turn off
        print("LEDs: Off")
        ep_led.set_gimbal_led(r=0, g=0, b=0, effect=ep_led.EFFECT_OFF)

        print("\n✓ LED tests completed!")

    except Exception as e:
        print(f"\n✗ Error: {e}")

    finally:
        print("\nClosing connection...")
        ep_robot.close()
        print("Disconnected.")


if __name__ == "__main__":
    import sys

    # Default to "ap" mode (Direct WiFi)
    conn_type = sys.argv[1] if len(sys.argv) > 1 else "ap"

    print("=" * 50)
    print("DJI RoboMaster SDK Test")
    print("=" * 50)
    print(f"Connection type: {conn_type}")
    print("Make sure robot has space to move!")
    time.sleep(3)

    test_basic_movement(conn_type)
    # test_gimbal(conn_type)
    # test_leds(conn_type)
