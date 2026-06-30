"""RoboMaster S1 Robot Controller.

This module provides a Python interface to control the DJI RoboMaster S1 robot
via the official robomaster SDK.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from robomaster.robot import Robot
    from robomaster.chassis import Chassis
    from robomaster.gimbal import Gimbal
    from robomaster.led import Led

from robomaster import robot
from robomaster import led

logger = logging.getLogger(__name__)


class RoboMasterController:
    """Adapter for RoboMaster S1 robot connection and control.

    Handles connection management, chassis movement, gimbal control,
    and LED effects via the official robomaster SDK.
    """

    def __init__(self) -> None:
        """Initialize controller with no active connection."""
        self._robot: Robot | None = None
        self._chassis: Chassis | None = None
        self._gimbal: Gimbal | None = None
        self._led: Led | None = None
        self._is_connected = False

    @property
    def is_connected(self) -> bool:
        """Return True if robot is connected."""
        return self._is_connected

    @property
    def chassis(self) -> Chassis | None:
        """Return chassis controller or None if not connected."""
        return self._chassis

    @property
    def gimbal(self) -> Gimbal | None:
        """Return gimbal controller or None if not connected."""
        return self._gimbal

    @property
    def led(self) -> Led | None:
        """Return LED controller or None if not connected."""
        return self._led

    def connect(self, conn_type: str = "sta") -> bool:
        """Connect to the RoboMaster S1 robot.

        Args:
            conn_type: Connection mode - "sta" for router mode (default),
                      "ap" for direct connection mode.

        Returns:
            True if connection successful, False otherwise.
        """
        try:
            logger.info("Connecting to robot", extra={"conn_type": conn_type})
            self._robot = robot.Robot()
            self._robot.initialize(conn_type=conn_type)

            # Store component references for easy access
            self._chassis = self._robot.chassis
            self._gimbal = self._robot.gimbal
            self._led = self._robot.led

            self._is_connected = True
            logger.info("Robot connected successfully")
            return True

        except Exception as e:
            logger.error("Failed to connect to robot", extra={"error": str(e)})
            self._is_connected = False
            return False

    def disconnect(self) -> None:
        """Disconnect from the robot and release resources."""
        if self._robot:
            try:
                self._robot.close()
                logger.info("Robot disconnected")
            except Exception as e:
                logger.error("Error during disconnect", extra={"error": str(e)})
            finally:
                self._robot = None
                self._chassis = None
                self._gimbal = None
                self._led = None
                self._is_connected = False

    def move(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0,
        xy_speed: float = 0.5,
        z_speed: int = 30,
    ) -> None:
        """Move chassis to relative position.

        Args:
            x: Distance in meters along x-axis (forward/back), range [-5, 5]
            y: Distance in meters along y-axis (left/right), range [-5, 5]
            z: Rotation angle in degrees around z-axis, range [-1800, 1800]
            xy_speed: Movement speed in m/s, range [0.5, 2.0]
            z_speed: Rotation speed in deg/s, range [10, 540]
        """
        if not self._chassis:
            raise RuntimeError("Not connected to robot")

        action = self._chassis.move(x=x, y=y, z=z, xy_speed=xy_speed, z_speed=z_speed)
        action.wait_for_completed()
        logger.debug("Move completed", extra={"x": x, "y": y, "z": z})

    def set_led(
        self, component: str, r: int, g: int, b: int, effect: str = "on", freq: int = 1
    ) -> None:
        """Set LED color and effect.

        Args:
            component: LED component - "all", "top_all", "top_right", "top_left",
                      "bottom_all", "bottom_front", "bottom_back", "bottom_left", "bottom_right"
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
            effect: LED effect - "on", "off", "flash", "breath", "scrolling" (scrolling for gimbal only)
            freq: Flash frequency 1-10 (for flash effect only)
        """
        if not self._led:
            raise RuntimeError("Not connected to robot")

        self._led.set_led(comp=component, r=r, g=g, b=b, effect=effect, freq=freq)
        logger.debug(
            "LED set",
            extra={"component": component, "rgb": (r, g, b), "effect": effect},
        )

    def turn_off_leds(self) -> None:
        """Turn off all LEDs."""
        if self._led:
            self._led.set_led(comp="all", r=0, g=0, b=0, effect="off")
            logger.debug("LEDs turned off")


def demo_square_pattern() -> None:
    """Run a demo: move in square pattern with LED feedback.

    This demonstrates basic robot control:
    1. Connect to robot
    2. Turn on green LED
    3. Move in square (forward, turn x4)
    4. Turn on blue breathing LED
    5. Cleanup
    """
    ctrl = RoboMasterController()

    if not ctrl.connect("sta"):
        print("Failed to connect to robot")
        return

    try:
        # Green = ready (using bottom LEDs)
        ctrl.set_led("bottom_all", 0, 255, 0, "on")
        print("Starting square pattern...")

        # Move in square (forward 0.5m, turn 90 degrees x4)
        for i in range(4):
            print(f"  Side {i + 1}/4: Moving forward")
            ctrl.move(x=0.5, y=0, z=0, xy_speed=0.5)  # Forward 0.5m
            print(f"  Side {i + 1}/4: Turning")
            ctrl.move(x=0, y=0, z=90, z_speed=100)  # Rotate 90 degrees

        # Blue = complete
        ctrl.set_led("bottom_all", 0, 0, 255, "breath")
        print("Square pattern complete!")

    except Exception as e:
        logger.error("Demo failed", extra={"error": str(e)})
        print(f"Error: {e}")
    finally:
        ctrl.turn_off_leds()
        ctrl.disconnect()
        print("Disconnected")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run demo
    demo_square_pattern()
