#!/usr/bin/env python3
"""
Simple connection test for RoboMasterPy.
Run this first to verify your setup.
"""

import sys
import argparse
import robomasterpy as rm


def test_connection(ip: str = "", timeout: float = 10.0) -> bool:
    """
    Test basic connection to RoboMaster.

    Args:
        ip: Robot IP (empty for auto-detect, 192.168.42.2 for USB, 192.168.2.1 for Direct)
        timeout: Connection timeout in seconds

    Returns:
        True if connection successful
    """
    print(f"Testing connection to RoboMaster...")
    print(f"  IP: {ip or '(auto-detect)'}")
    print(f"  Timeout: {timeout}s")
    print()

    try:
        print("Creating Commander...")
        cmd = rm.Commander(ip=ip, timeout=timeout)

        print("✓ Connected!")
        print()

        # Get basic info
        print("--- Robot Info ---")
        print(f"IP: {cmd.get_ip()}")
        print(f"SDK Version: {cmd.version()}")
        print(f"Robot Mode: {cmd.get_robot_mode()}")

        # Get chassis status
        try:
            status = cmd.get_chassis_status()
            print(f"Chassis Status: {status}")
        except Exception as e:
            print(f"Chassis Status: Could not query ({e})")

        # Get position
        try:
            pos = cmd.get_chassis_position()
            print(f"Position: x={pos.x:.3f}m, y={pos.y:.3f}m, z={pos.z:.3f}°")
        except Exception as e:
            print(f"Position: Could not query ({e})")

        # Get attitude
        try:
            att = cmd.get_chassis_attitude()
            print(
                f"Attitude: pitch={att.pitch:.2f}°, roll={att.roll:.2f}°, yaw={att.yaw:.2f}°"
            )
        except Exception as e:
            print(f"Attitude: Could not query ({e})")

        cmd.close()
        print()
        print("✓ Connection test PASSED")
        return True

    except ConnectionRefusedError:
        print("✗ Connection refused - is the robot powered on and in SDK mode?")
        print("  1. Check robot is powered on")
        print("  2. Verify SDK mode is enabled in RoboMaster App")
        print("  3. Check IP address is correct")
        return False

    except TimeoutError:
        print("✗ Connection timeout - robot not responding")
        print("  1. Check network connection (ping the robot IP)")
        print("  2. Verify SDK mode is enabled")
        print("  3. Try increasing timeout")
        return False

    except Exception as e:
        print(f"✗ Connection failed: {type(e).__name__}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test RoboMaster connection")
    parser.add_argument(
        "--ip",
        default="",
        help="Robot IP (192.168.42.2 for USB, 192.168.2.1 for Direct, empty for auto)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Connection timeout in seconds (default: 10)",
    )
    parser.add_argument(
        "--usb", action="store_true", help="Use USB mode IP (192.168.42.2)"
    )
    parser.add_argument(
        "--direct", action="store_true", help="Use Direct WiFi mode IP (192.168.2.1)"
    )

    args = parser.parse_args()

    # Determine IP
    ip = args.ip
    if args.usb:
        ip = "192.168.42.2"
    elif args.direct:
        ip = "192.168.2.1"

    # Run test
    success = test_connection(ip=ip, timeout=args.timeout)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
