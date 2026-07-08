#!/usr/bin/env python3
"""
Gimbal test using official DJI SDK.
Based on gimbal.py - tests gimbal movement patterns.
"""

from robomaster import robot
import time


def main():
    print("=" * 50)
    print("RoboMaster S1 Gimbal Test")
    print("=" * 50)
    print("\n⚠️  Ensure gimbal has clearance to move!")
    print("Starting in 3 seconds...")
    time.sleep(3)

    print("\nConnecting to robot...")
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    print("✓ Connected!")

    ep_gimbal = ep_robot.gimbal

    try:
        print("\n--- Starting Gimbal Sequence ---")

        # 1. Recenter
        print("1. Recentering gimbal...")
        ep_gimbal.moveto(pitch=0, yaw=0).wait_for_completed()
        time.sleep(0.5)

        # 2. Look up and right
        print("2. Moving to pitch=15, yaw=90...")
        ep_gimbal.moveto(
            pitch=15, yaw=90, pitch_speed=50, yaw_speed=100
        ).wait_for_completed()
        time.sleep(0.5)

        # 3. Look down and left
        print("3. Moving to pitch=-15, yaw=-90...")
        ep_gimbal.moveto(
            pitch=-15, yaw=-90, pitch_speed=100, yaw_speed=30
        ).wait_for_completed()
        time.sleep(0.5)

        # 4. Back to center
        print("4. Back to center...")
        ep_gimbal.moveto(pitch=0, yaw=0).wait_for_completed()
        time.sleep(0.5)

        # 5. Relative moves - look left 3 times
        print("5. Looking left (30° x 3)...")
        for i in range(3):
            ep_gimbal.move(pitch=0, yaw=30).wait_for_completed()
            time.sleep(0.3)

        # 6. Relative moves - look right 3 times
        print("6. Looking right (30° x 3)...")
        for i in range(3):
            ep_gimbal.move(pitch=0, yaw=-30).wait_for_completed()
            time.sleep(0.3)

        # 7. Look up
        print("7. Looking up (20°)...")
        ep_gimbal.move(pitch=20, yaw=0).wait_for_completed()
        time.sleep(0.5)

        # 8. Look down
        print("8. Looking down (20°)...")
        ep_gimbal.move(pitch=-20, yaw=0).wait_for_completed()
        time.sleep(0.5)

        # 9. Final recenter
        print("9. Final recenter...")
        ep_gimbal.moveto(pitch=0, yaw=0).wait_for_completed()

        print("\n✓ All gimbal movements completed!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        print("\nClosing connection...")
        ep_robot.close()
        print("✓ Disconnected.")
        print("=" * 50)


if __name__ == "__main__":
    main()
