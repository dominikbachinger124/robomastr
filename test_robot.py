#!/usr/bin/env python3
"""
Test script for RoboMaster S1 using official DJI SDK.
Based on move2.py - tests basic chassis movement.
"""

from robomaster import robot
import time


def main():
    print("=" * 50)
    print("RoboMaster S1 Movement Test")
    print("=" * 50)
    print("\n⚠️  SAFETY: Ensure robot has clearance to move!")
    print("Starting in 3 seconds...")
    time.sleep(3)

    # Initialize robot connection
    print("\nConnecting to robot...")
    ep_robot = robot.Robot()

    # Connection types:
    # "ap" = Direct WiFi (robot as access point)
    # "sta" = Station mode (robot connects to router)
    # "rndis" = USB cable connection
    ep_robot.initialize(conn_type="ap")
    print("✓ Connected!")

    # Get chassis control
    ep_chassis = ep_robot.chassis

    # Movement parameters
    x_val = 0.5  # meters forward/backward
    y_val = 0.6  # meters left/right
    z_val = 90  # degrees rotation
    xy_speed = 0.5  # m/s (AI safety limit)
    z_speed = 45  # deg/s

    try:
        print("\n--- Starting Movement Sequence ---")

        # Forward
        print(f"1. Moving forward {x_val}m...")
        ep_chassis.move(x=x_val, y=0, z=0, xy_speed=xy_speed).wait_for_completed()
        time.sleep(0.5)

        # Backward
        print(f"2. Moving backward {x_val}m...")
        ep_chassis.move(x=-x_val, y=0, z=0, xy_speed=xy_speed).wait_for_completed()
        time.sleep(0.5)

        # Left
        print(f"3. Moving left {y_val}m...")
        ep_chassis.move(x=0, y=-y_val, z=0, xy_speed=xy_speed).wait_for_completed()
        time.sleep(0.5)

        # Right
        print(f"4. Moving right {y_val}m...")
        ep_chassis.move(x=0, y=y_val, z=0, xy_speed=xy_speed).wait_for_completed()
        time.sleep(0.5)

        # Rotate left
        print(f"5. Rotating left {z_val}°...")
        ep_chassis.move(x=0, y=0, z=z_val, z_speed=z_speed).wait_for_completed()
        time.sleep(0.5)

        # Rotate right
        print(f"6. Rotating right {z_val}°...")
        ep_chassis.move(x=0, y=0, z=-z_val, z_speed=z_speed).wait_for_completed()
        time.sleep(0.5)

        print("\n✓ All movements completed successfully!")

    except Exception as e:
        print(f"\n✗ Error during movement: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Always close connection
        print("\nClosing connection...")
        ep_robot.close()
        print("✓ Disconnected.")
        print("=" * 50)


if __name__ == "__main__":
    main()
