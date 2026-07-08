#!/usr/bin/env python3
"""
LED test using official DJI SDK.
Tests gimbal and chassis LEDs with different colors and effects.
"""

from robomaster import robot, led
import time


def main():
    print("=" * 50)
    print("RoboMaster S1 - LED Test")
    print("=" * 50)
    print("\n⚠️  Watch the robot LEDs!")
    time.sleep(2)

    print("\nConnecting...")
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    print("✓ Connected!")

    ep_led = ep_robot.led

    try:
        print("\n--- Gimbal LEDs ---")

        # Red
        print("→ Gimbal: Red")
        ep_led.set_gimbal_led(r=255, g=0, b=0, effect=led.EFFECT_ON)
        time.sleep(1)

        # Green
        print("→ Gimbal: Green")
        ep_led.set_gimbal_led(r=0, g=255, b=0, effect=led.EFFECT_ON)
        time.sleep(1)

        # Blue
        print("→ Gimbal: Blue")
        ep_led.set_gimbal_led(r=0, g=0, b=255, effect=led.EFFECT_ON)
        time.sleep(1)

        # Flash yellow
        print("→ Gimbal: Flash Yellow")
        ep_led.set_gimbal_led(r=255, g=255, b=0, effect=led.EFFECT_FLASH)
        time.sleep(2)

        # Off
        print("→ Gimbal: Off")
        ep_led.set_gimbal_led(r=0, g=0, b=0, effect=led.EFFECT_OFF)
        time.sleep(0.5)

        print("\n--- Chassis LEDs ---")

        # All red
        print("→ Chassis: Red")
        ep_led.set_led(comp=led.COMP_ALL, r=255, g=0, b=0, effect=led.EFFECT_ON)
        time.sleep(1)

        # All green
        print("→ Chassis: Green")
        ep_led.set_led(comp=led.COMP_ALL, r=0, g=255, b=0, effect=led.EFFECT_ON)
        time.sleep(1)

        # All blue
        print("→ Chassis: Blue")
        ep_led.set_led(comp=led.COMP_ALL, r=0, g=0, b=255, effect=led.EFFECT_ON)
        time.sleep(1)

        # All off
        print("→ Chassis: Off")
        ep_led.set_led(comp=led.COMP_ALL, r=0, g=0, b=0, effect=led.EFFECT_OFF)

        print("\n✓ LED test complete!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        print("\nClosing...")
        ep_robot.close()
        print("✓ Done.")
        print("=" * 50)


if __name__ == "__main__":
    main()
