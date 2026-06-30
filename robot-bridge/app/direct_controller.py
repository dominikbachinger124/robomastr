"""RoboMaster S1 Direct Connection Controller.

Für Nutzung OHNE RoboMaster App (App wurde eingestellt).
Nutzt Direct Connection Mode (AP Mode) statt Router Mode.
"""

from __future__ import annotations

import logging
import socket
import time
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from robomaster.robot import Robot
    from robomaster.chassis import Chassis
    from robomaster.gimbal import Gimbal
    from robomaster.led import Led

from robomaster import robot
from robomaster import config

logger = logging.getLogger(__name__)


class RoboMasterDirectController:
    """RoboMaster S1 Controller für Direct Connection Mode.

    Nutzung ohne RoboMaster App - die App wurde 2020 eingestellt.

    Setup:
    1. Schalter am Smart Central Control auf "Direct Connection" stellen
    2. PC mit RoboMaster WiFi verbinden (SSID: RoboMaster_S1_XXXXXX)
    3. Diesen Controller nutzen

    Default IP in Direct Mode: 192.168.2.1
    Port: 40923
    """

    # Direct Connection Default Settings
    DEFAULT_IP = "192.168.2.1"
    DEFAULT_PORT = 40923

    def __init__(self, robot_ip: str = DEFAULT_IP) -> None:
        """Initialize controller.

        Args:
            robot_ip: IP address of robot in direct mode (default: 192.168.2.1)
        """
        self._robot: Robot | None = None
        self._chassis: Chassis | None = None
        self._gimbal: Gimbal | None = None
        self._led: Led | None = None
        self._is_connected = False
        self._robot_ip = robot_ip

        # Set local IP for direct connection (autodetect might fail)
        # The robot is at 192.168.2.1, we need to be in 192.168.2.x range
        config.LOCAL_IP_STR = self._get_local_ip()

    def _get_local_ip(self) -> str:
        """Get local IP in robot's subnet."""
        try:
            # Try to detect IP when connected to robot's WiFi
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((self._robot_ip, 40923))
            local_ip = s.getsockname()[0]
            s.close()
            logger.info(f"Local IP detected: {local_ip}")
            return local_ip
        except Exception as e:
            logger.warning(f"Could not detect IP, using default: {e}")
            return "192.168.2.20"  # Default fallback

    @property
    def is_connected(self) -> bool:
        """Return True if robot is connected."""
        return self._is_connected

    def connect(self) -> bool:
        """Connect to robot in Direct Connection Mode (AP Mode).

        Returns:
            True if connection successful, False otherwise.
        """
        try:
            logger.info(
                "Connecting to RoboMaster S1 (Direct Connection)",
                extra={"ip": self._robot_ip},
            )

            self._robot = robot.Robot()
            # conn_type='ap' = Access Point / Direct Connection Mode
            self._robot.initialize(conn_type="ap")

            self._chassis = self._robot.chassis
            self._gimbal = self._robot.gimbal
            self._led = self._robot.led

            self._is_connected = True

            # Get robot info
            version = self._robot.get_version()
            sn = self._robot.get_sn()
            logger.info(f"Robot connected - Version: {version}, SN: {sn}")

            return True

        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self._is_connected = False
            return False

    def disconnect(self) -> None:
        """Disconnect from robot."""
        if self._robot:
            try:
                self._robot.close()
                logger.info("Disconnected")
            except Exception as e:
                logger.error(f"Disconnect error: {e}")
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
            x: Distance in meters (forward/back), range [-5, 5]
            y: Distance in meters (left/right), range [-5, 5]
            z: Rotation angle in degrees, range [-1800, 1800]
            xy_speed: Movement speed m/s, range [0.5, 2.0] (AI safety: 0.5 max)
            z_speed: Rotation speed deg/s, range [10, 540]
        """
        if not self._chassis:
            raise RuntimeError("Not connected")

        action = self._chassis.move(x=x, y=y, z=z, xy_speed=xy_speed, z_speed=z_speed)
        action.wait_for_completed()
        logger.debug(f"Move: x={x}, y={y}, z={z}")

    def move_forward(self, distance: float, speed: float = 0.5) -> None:
        """Move forward by distance.

        Args:
            distance: Distance in meters (positive = forward)
            speed: Speed in m/s (max 0.5 for AI safety)
        """
        self.move(x=distance, xy_speed=speed)

    def rotate(self, degrees: float, speed: int = 100) -> None:
        """Rotate in place.

        Args:
            degrees: Rotation in degrees (positive = clockwise)
            speed: Rotation speed deg/s (10-540)
        """
        self.move(z=degrees, z_speed=speed)

    def stop(self) -> None:
        """Stop all chassis movement."""
        if self._chassis:
            self._chassis.drive_speed(x=0, y=0, z=0)
            logger.debug("Emergency stop")

    def set_led(
        self, component: str, r: int, g: int, b: int, effect: str = "on"
    ) -> None:
        """Set LED color.

        Args:
            component: "all", "top_all", "bottom_all", etc.
            r, g, b: RGB values 0-255
            effect: "on", "off", "flash", "breath"
        """
        if not self._led:
            raise RuntimeError("Not connected")
        self._led.set_led(comp=component, r=r, g=g, b=b, effect=effect)

    def turn_off_leds(self) -> None:
        """Turn off all LEDs."""
        if self._led:
            self._led.set_led(comp="all", r=0, g=0, b=0, effect="off")

    def get_battery(self) -> int:
        """Get battery percentage.

        Returns:
            Battery level 0-100
        """
        if self._robot:
            return self._robot.battery.get_battery()
        return -1


def demo_direct_connection():
    """Demo für Direct Connection Mode.

    Voraussetzungen:
    1. RoboMaster einschalten
    2. Schalter auf "Direct Connection" stellen
    3. PC mit RoboMaster WiFi verbinden
    """
    print("=" * 50)
    print("RoboMaster S1 - Direct Connection Demo")
    print("=" * 50)
    print()
    print("Voraussetzungen:")
    print("1. RoboMaster S1 einschalten")
    print("2. Schalter auf 'Direct Connection' stellen")
    print("3. PC mit RoboMaster WiFi verbinden")
    print()

    ctrl = RoboMasterDirectController()

    print("Verbinde mit RoboMaster...")
    if not ctrl.connect():
        print("❌ Verbindung fehlgeschlagen!")
        print("Tipps:")
        print("- Prüfe ob Schalter auf 'Direct Connection' steht")
        print("- Prüfe ob PC mit RoboMaster WiFi verbunden ist")
        print("- Standard-IP: 192.168.2.1")
        return

    print("✅ Verbunden!")

    try:
        # Battery check
        battery = ctrl.get_battery()
        print(f"🔋 Batterie: {battery}%")

        # Green LED = ready
        ctrl.set_led("bottom_all", 0, 255, 0, "on")
        print("🟢 LED: Grün (Bereit)")

        # Demo sequence
        print("\nStarte Demo...")
        print("1. Vorwärts 0.5m")
        ctrl.move_forward(0.5, speed=0.3)

        print("2. 90° Drehung")
        ctrl.rotate(90, speed=50)

        print("3. Zurück 0.5m")
        ctrl.move_forward(-0.5, speed=0.3)

        print("4. Zurück zur Startposition")
        ctrl.rotate(-90, speed=50)

        # Blue LED = complete
        ctrl.set_led("bottom_all", 0, 0, 255, "breath")
        print("\n🔵 LED: Blau (Demo abgeschlossen)")
        print("✅ Demo erfolgreich!")

    except Exception as e:
        print(f"❌ Fehler: {e}")
    finally:
        ctrl.turn_off_leds()
        ctrl.disconnect()
        print("\nVerbindung getrennt")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    demo_direct_connection()
