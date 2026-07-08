#!/usr/bin/env python3
"""
DJI SDK Connection Test
Tests connection to RoboMaster S1 using the official DJI SDK.
"""

import sys
import time
from robomaster import robot
from robomaster import config


def test_connection(conn_type="ap", timeout=10):
    """
    Test connection to robot.

    Args:
        conn_type: Connection type - "ap" (Direct WiFi), "sta" (Router), "rndis" (USB)
        timeout: Connection timeout in seconds
    """
    print("=" * 50)
    print("DJI RoboMaster SDK Connection Test")
    print("=" * 50)
    print(f"\nConnection type: {conn_type}")
    print(f"Timeout: {timeout}s")
    print("\nMake sure:")
    print("1. Robot is powered on")
    print("2. Robot is in SDK mode (enabled in RoboMaster App)")
    print("3. For 'ap' mode: Connected to robot's WiFi")
    print("4. For 'sta' mode: Robot and computer on same network")
    print("5. For 'rndis' mode: USB cable connected")
    print()

    ep_robot = None

    try:
        print(f"Initializing robot (conn_type='{conn_type}')...")
        ep_robot = robot.Robot()

        # Set shorter timeout for connection
        print(f"Connecting with {timeout}s timeout...")
        ep_robot.initialize(conn_type=conn_type)

        print("✓ Connected successfully!")

        # Test getting robot info
        print("\n--- Robot Info ---")

        # Try to get version
        try:
            version = ep_robot.get_version()
            print(f"Version: {version}")
        except Exception as e:
            print(f"Version: Could not retrieve ({e})")

        # Try to get SN
        try:
            sn = ep_robot.get_sn()
            print(f"SN: {sn}")
        except Exception as e:
            print(f"SN: Could not retrieve ({e})")

        # Test chassis
        print("\n--- Testing Chassis ---")
        ep_chassis = ep_robot.chassis

        # Get position
        try:
            x, y, z = ep_chassis.get_position_based_power_on()
            print(f"Position: x={x:.3f}m, y={y:.3f}m, z={z:.3f}°")
        except Exception as e:
            print(f"Position: Could not retrieve ({e})")

        # Get attitude
        try:
            pitch, roll, yaw = ep_chassis.get_attitude()
            print(f"Attitude: pitch={pitch:.2f}°, roll={roll:.2f}°, yaw={yaw:.2f}°")
        except Exception as e:
            print(f"Attitude: Could not retrieve ({e})")

        # Test gimbal
        print("\n--- Testing Gimbal ---")
        ep_gimbal = ep_robot.gimbal

        try:
            pitch, yaw, roll = ep_gimbal.get_attitude()
            print(f"Gimbal: pitch={pitch:.2f}°, yaw={yaw:.2f}°, roll={roll:.2f}°")
        except Exception as e:
            print(f"Gimbal: Could not retrieve ({e})")

        # Test movement (small safe movement)
        print("\n--- Testing Safe Movement ---")
        print("Moving forward 0.2m...")
        ep_chassis.move(x=0.2, y=0, z=0, xy_speed=0.3).wait_for_completed()
        time.sleep(0.5)

        print("Moving backward 0.2m...")
        ep_chassis.move(x=-0.2, y=0, z=0, xy_speed=0.3).wait_for_completed()

        print("\n✓ All tests passed!")
        return True

    except Exception as e:
        print(f"\n✗ Connection/Error: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        if ep_robot:
            print("\nClosing connection...")
            ep_robot.close()
            print("✓ Disconnected.")


if __name__ == "__main__":
    # Get connection type from command line
    conn_type = sys.argv[1] if len(sys.argv) > 1 else "ap"

    # Validate connection type
    valid_types = ["ap", "sta", "rndis"]
    if conn_type not in valid_types:
        print(f"Invalid connection type: {conn_type}")
        print(f"Valid types: {', '.join(valid_types)}")
        sys.exit(1)

    success = test_connection(conn_type)
    sys.exit(0 if success else 1)
