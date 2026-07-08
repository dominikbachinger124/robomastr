#!/usr/bin/env python3
"""
Simple Gimbal test - shorter movements, faster execution.
Based on gimbal.py pattern.
"""

from robomaster import robot
import time


def main():
    print("=" * 50)
    print("RoboMaster S1 - Simple Gimbal Test")
    print("=" * 50)
    print("\n⚠️  Ensure gimbal has clearance!")
    time.sleep(2)

    print("\nConnecting...")
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    print("✓ Connected!")

    ep_gimbal = ep_robot.gimbal

    # Simple sequence - smaller angles
    moves = [
        ("Recenter", lambda: ep_gimbal.moveto(pitch=0, yaw=0)),
        ("Look up 10°", lambda: ep_gimbal.moveto(pitch=10, yaw=0)),
        ("Look down 10°", lambda: ep_gimbal.moveto(pitch=-10, yaw=0)),
        ("Look left 30°", lambda: ep_gimbal.moveto(pitch=0, yaw=-30)),
        ("Look right 30°", lambda: ep_gimbal.moveto(pitch=0, yaw=30)),
        ("Back to center", lambda: ep_gimbal.moveto(pitch=0, yaw=0)),
    ]

    try:
        for name, move_func in moves:
            print(f"\n→ {name}...")
            try:
                move_func().wait_for_completed()
                time.sleep(0.3)
            except Exception as e:
                print(f"  ⚠️  Skipped: {e}")
                continue

        print("\n✓ Gimbal test complete!")

    except Exception as e:
        print(f"\n✗ Error: {e}")

    finally:
        print("\nClosing...")
        ep_robot.close()
        print("✓ Done.")


if __name__ == "__main__":
    main()
