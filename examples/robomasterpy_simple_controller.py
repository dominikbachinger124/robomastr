#!/usr/bin/env python3
"""
RoboMasterPy Simple Controller

A clean, reusable controller class for the RoboMaster S1.
Uses the SDK approach (simpler than the full framework).
"""

import time
from typing import Optional, Tuple
import robomasterpy as rm


class RoboMasterController:
    """
    Simple controller for DJI RoboMaster S1 using RoboMasterPy.

    Example:
        with RoboMasterController("192.168.42.2") as robot:
            robot.move_forward(0.5, 1.0)  # 0.5 m/s for 1 second
            robot.rotate(90)  # Rotate 90 degrees
    """

    # Safety limits
    MAX_SPEED_MPS = 0.5  # m/s for AI-controlled operations
    MAX_ROTATION_SPEED = 100  # deg/s

    def __init__(self, ip: str = "", timeout: float = 30.0):
        """
        Initialize controller.

        Args:
            ip: Robot IP. Use "192.168.42.2" for USB, "192.168.2.1" for Direct WiFi,
                or "" for auto-detect in router mode.
            timeout: Connection timeout in seconds.
        """
        self.ip = ip
        self.timeout = timeout
        self._cmd: Optional[rm.Commander] = None
        self._connected = False

    def connect(self) -> bool:
        """Connect to the robot."""
        try:
            self._cmd = rm.Commander(ip=self.ip, timeout=self.timeout)
            self._connected = True
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect and cleanup."""
        if self._cmd:
            self.stop()  # Emergency stop
            self._cmd.close()
            self._connected = False

    def __enter__(self):
        """Context manager entry."""
        if not self.connect():
            raise ConnectionError("Failed to connect to robot")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
        return False

    # --- Movement Commands ---

    def stop(self) -> None:
        """Emergency stop all movement."""
        if self._cmd:
            self._cmd.chassis_speed(x=0, y=0, z=0)

    def move_speed(self, x: float = 0, y: float = 0, z: float = 0) -> None:
        """
        Set chassis speed.

        Args:
            x: Forward/backward speed in m/s (-3.5 to 3.5)
            y: Left/right speed in m/s (-3.5 to 3.5)
            z: Rotation speed in deg/s (-600 to 600)
        """
        # Apply safety limits
        x = max(-self.MAX_SPEED_MPS, min(self.MAX_SPEED_MPS, x))
        y = max(-self.MAX_SPEED_MPS, min(self.MAX_SPEED_MPS, y))
        z = max(-self.MAX_ROTATION_SPEED, min(self.MAX_ROTATION_SPEED, z))

        self._cmd.chassis_speed(x=x, y=y, z=z)

    def move_forward(self, speed: float = 0.3, duration: float = 1.0) -> None:
        """Move forward at specified speed for duration."""
        self.move_speed(x=speed)
        time.sleep(duration)
        self.stop()

    def move_backward(self, speed: float = 0.3, duration: float = 1.0) -> None:
        """Move backward at specified speed for duration."""
        self.move_speed(x=-speed)
        time.sleep(duration)
        self.stop()

    def rotate(self, degrees: float, speed: float = 60) -> None:
        """
        Rotate by specified degrees.

        Args:
            degrees: Degrees to rotate (positive = clockwise)
            speed: Rotation speed in deg/s
        """
        self._cmd.chassis_move(z=degrees, speed_z=speed)
        time.sleep(abs(degrees) / speed + 0.5)  # Wait for completion

    def rotate_continuous(self, speed: float = 30) -> None:
        """Start continuous rotation."""
        self.move_speed(z=speed)

    # --- Gimbal Commands ---

    def gimbal_recenter(self) -> None:
        """Recenter the gimbal."""
        self._cmd.gimbal_recenter()

    def gimbal_move(
        self,
        pitch: float = 0,
        yaw: float = 0,
        pitch_speed: float = 30,
        yaw_speed: float = 60,
    ) -> None:
        """
        Move gimbal relative to current position.

        Args:
            pitch: Pitch change in degrees (-55 to 55)
            yaw: Yaw change in degrees (-250 to 250)
            pitch_speed: Speed in deg/s
            yaw_speed: Speed in deg/s
        """
        self._cmd.gimbal_move(
            pitch=pitch, yaw=yaw, pitch_speed=pitch_speed, yaw_speed=yaw_speed
        )

    def gimbal_moveto(
        self,
        pitch: float = 0,
        yaw: float = 0,
        pitch_speed: float = 30,
        yaw_speed: float = 60,
    ) -> None:
        """
        Move gimbal to absolute position (from center).

        Args:
            pitch: Target pitch in degrees (-55 to 55, 0 = level)
            yaw: Target yaw in degrees (-250 to 250, 0 = center)
        """
        self._cmd.gimbal_moveto(
            pitch=pitch, yaw=yaw, pitch_speed=pitch_speed, yaw_speed=yaw_speed
        )

    def gimbal_speed(self, pitch: float = 0, yaw: float = 0) -> None:
        """Set continuous gimbal rotation speed."""
        self._cmd.gimbal_speed(pitch=pitch, yaw=yaw)

    # --- LED Commands ---

    def set_led(
        self,
        r: int,
        g: int,
        b: int,
        component: str = rm.LED_ALL,
        effect: str = rm.LED_EFFECT_ON,
    ) -> None:
        """
        Set LED color.

        Args:
            r, g, b: RGB values (0-255)
            component: LED component (LED_ALL, LED_TOP_ALL, LED_BOTTOM_ALL, etc.)
            effect: LED effect (LED_EFFECT_ON, LED_EFFECT_OFF, LED_EFFECT_FLASH, LED_EFFECT_BREATH)
        """
        self._cmd.led_control(comp=component, effect=effect, r=r, g=g, b=b)

    def led_off(self) -> None:
        """Turn off all LEDs."""
        self.set_led(0, 0, 0, effect=rm.LED_EFFECT_OFF)

    # --- Blaster ---

    def blaster_fire(self) -> None:
        """Fire the blaster once."""
        self._cmd.blaster_fire()

    # --- Queries ---

    def get_battery(self) -> str:
        """Get battery status."""
        return self._cmd.get_chassis_status()

    def get_position(self) -> Tuple[float, float, float]:
        """Get chassis position (x, y, z in meters/degrees)."""
        pos = self._cmd.get_chassis_position()
        return (pos.x, pos.y, pos.z)

    def get_attitude(self) -> Tuple[float, float, float]:
        """Get chassis attitude (pitch, roll, yaw in degrees)."""
        att = self._cmd.get_chassis_attitude()
        return (att.pitch, att.roll, att.yaw)

    def get_gimbal_attitude(self) -> Tuple[float, float]:
        """Get gimbal attitude (pitch, yaw in degrees)."""
        att = self._cmd.get_gimbal_attitude()
        return (att.pitch, att.yaw)

    # --- Mode Settings ---

    def set_mode_chassis_lead(self) -> None:
        """Set robot mode to chassis_lead (chassis controls gimbal direction)."""
        self._cmd.robot_mode(rm.MODE_CHASSIS_LEAD)

    def set_mode_gimbal_lead(self) -> None:
        """Set robot mode to gimbal_lead (gimbal direction is forward)."""
        self._cmd.robot_mode(rm.MODE_GIMBAL_LEAD)

    def set_mode_free(self) -> None:
        """Set robot mode to free (chassis and gimbal independent)."""
        self._cmd.robot_mode(rm.MODE_FREE)


def demo():
    """Demo using the controller."""
    # Update this to your robot's IP
    ROBOT_IP = "192.168.42.2"  # USB mode
    # ROBOT_IP = "192.168.2.1"  # Direct WiFi mode
    # ROBOT_IP = ""  # Router mode (auto-detect)

    print("RoboMasterPy Controller Demo")
    print("Make sure robot has space to move!")
    time.sleep(3)

    with RoboMasterController(ROBOT_IP) as robot:
        print("\n1. Testing LEDs...")
        robot.set_led(255, 0, 0)  # Red
        time.sleep(0.5)
        robot.set_led(0, 255, 0)  # Green
        time.sleep(0.5)
        robot.set_led(0, 0, 255)  # Blue
        time.sleep(0.5)
        robot.led_off()

        print("\n2. Testing Gimbal...")
        robot.gimbal_recenter()
        time.sleep(1)
        robot.gimbal_move(pitch=-20)  # Look down
        time.sleep(1)
        robot.gimbal_recenter()

        print("\n3. Testing Movement...")
        robot.set_mode_chassis_lead()

        print("   Moving forward...")
        robot.move_forward(speed=0.2, duration=1.0)
        time.sleep(0.5)

        print("   Rotating...")
        robot.rotate(90, speed=60)
        time.sleep(0.5)

        print("\n4. Reading sensors...")
        pos = robot.get_position()
        att = robot.get_attitude()
        print(f"   Position: x={pos[0]:.2f}, y={pos[1]:.2f}, z={pos[2]:.2f}")
        print(f"   Attitude: pitch={att[0]:.2f}, roll={att[1]:.2f}, yaw={att[2]:.2f}")

        print("\nDemo complete!")


if __name__ == "__main__":
    demo()
