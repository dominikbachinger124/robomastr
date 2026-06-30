"""RoboMaster S1 Simple TCP Controller.

KORREKTE Methode für S1 - nutzt direktes TCP Protokoll, NICHT das SDK!

Das offizielle DJI SDK ist für EP/EP Core, nicht für S1.
Der S1 nutzt ein einfaches text-basiertes Protokoll.

Protokoll:
- TCP Verbindung zu Port 40923
- Befehle werden als Text gesendet, enden mit ';'
- Antworten kommen als Text zurück

Beispiel:
    >>> send("command")  # Enter SDK mode
    >>> send("chassis move x 1")  # Move forward 1m

WICHTIG: Der S1 akzeptiert Verbindungen NUR im Direct Connection Mode!
Schalter muss auf Direct Connection stehen (nicht Router).
"""

import socket
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class RoboMasterSimpleController:
    """Einfacher TCP-Controller für RoboMaster S1.

    Nutzt das korrekte Protokoll für S1 (nicht das EP SDK).

    Example:
        >>> ctrl = RoboMasterSimpleController("192.168.42.2")
        >>> ctrl.connect()
        >>> ctrl.send_command("chassis move x 1")
        >>> ctrl.close()
    """

    def __init__(self, host: str = "192.168.42.2", port: int = 40923):
        """Initialize controller.

        Args:
            host: IP address of robot
                  - USB: 192.168.42.2
                  - WiFi Direct: 192.168.2.1
            port: Always 40923 for S1
        """
        self.host = host
        self.port = port
        self._socket: Optional[socket.socket] = None
        self._connected = False

    def connect(self) -> bool:
        """Connect to robot via TCP.

        Returns:
            True if connected successfully
        """
        try:
            logger.info(f"Connecting to {self.host}:{self.port}...")

            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(5)
            self._socket.connect((self.host, self.port))

            # Enter SDK mode (required!)
            response = self.send_command("command")

            if "ok" in response.lower() or "ok" in response:
                self._connected = True
                logger.info("✅ Connected and in SDK mode")
                return True
            else:
                logger.warning(f"Unexpected response to 'command': {response}")
                # Try anyway
                self._connected = True
                return True

        except socket.timeout:
            logger.error("❌ Connection timeout - is robot powered on?")
            return False
        except ConnectionRefusedError:
            logger.error("❌ Connection refused - is robot in Direct Connection mode?")
            logger.error("   Check: Schalter muss auf 'Direct Connection' stehen!")
            return False
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False

    def send_command(self, cmd: str) -> str:
        """Send command to robot.

        Args:
            cmd: Command string (without trailing ';')

        Returns:
            Response from robot
        """
        if not self._socket:
            raise RuntimeError("Not connected")

        # Add semicolon suffix (required!)
        full_cmd = cmd + ";"

        logger.debug(f"Sending: {cmd}")
        self._socket.send(full_cmd.encode("utf-8"))

        try:
            response = self._socket.recv(1024).decode("utf-8")
            logger.debug(f"Response: {response}")
            return response
        except socket.timeout:
            logger.warning("No response (timeout)")
            return ""

    def close(self):
        """Close connection."""
        if self._socket:
            try:
                self.send_command("quit")
            except:
                pass
            self._socket.close()
            self._socket = None
            self._connected = False
            logger.info("Disconnected")

    # Convenience methods
    def move_forward(self, distance: float, speed: float = 0.5):
        """Move forward by distance (meters)."""
        return self.send_command(f"chassis move x {distance} vxy {speed}")

    def move_backward(self, distance: float, speed: float = 0.5):
        """Move backward by distance."""
        return self.send_command(f"chassis move x -{distance} vxy {speed}")

    def move_left(self, distance: float, speed: float = 0.5):
        """Move left."""
        return self.send_command(f"chassis move y {distance} vxy {speed}")

    def move_right(self, distance: float, speed: float = 0.5):
        """Move right."""
        return self.send_command(f"chassis move y -{distance} vxy {speed}")

    def rotate(self, degrees: float, speed: int = 100):
        """Rotate in place.

        Args:
            degrees: Positive = clockwise, negative = counter-clockwise
            speed: Rotation speed (10-540 deg/s)
        """
        return self.send_command(f"chassis move z {degrees} vz {speed}")

    def stop(self):
        """Stop all movement immediately."""
        return self.send_command("chassis wheel w1 0 w2 0 w3 0 w4 0")

    def set_led(self, r: int, g: int, b: int):
        """Set LED color (RGB 0-255)."""
        return self.send_command(f"led control comp all r {r} g {g} b {b}")

    def get_battery(self):
        """Get battery percentage."""
        response = self.send_command("chassis battery ?")
        return response

    def get_version(self):
        """Get robot version."""
        return self.send_command("version ?")


def demo():
    """Demo für einfachen TCP-Controller."""
    import sys

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    print("=" * 60)
    print("🤖 RoboMaster S1 - Simple TCP Controller Demo")
    print("=" * 60)
    print()
    print("WICHTIGE Voraussetzungen:")
    print("1. RoboMaster S1 eingeschaltet")
    print("2. Schalter auf 'Direct Connection' (NICHT Router!)")
    print("3. USB-Kabel verbunden ODER WiFi verbunden")
    print()

    # Try USB first, then WiFi
    host = input("IP-Adresse [192.168.42.2 für USB]: ").strip()
    if not host:
        host = "192.168.42.2"

    print(f"\nVerbinde zu {host}...")

    ctrl = RoboMasterSimpleController(host)

    if not ctrl.connect():
        print("\n❌ Verbindung fehlgeschlagen!")
        print("\nTipps:")
        print("• Ist der Schalter auf 'Direct Connection'?")
        print("• Ist das USB-Kabel in der OBEREN Einheit?")
        print("• 10 Sekunden nach dem Einschalten gewartet?")
        print("• Versuche WiFi: 192.168.2.1")
        sys.exit(1)

    print("\n✅ Verbunden!")
    print()

    try:
        # Get version
        print("📋 Robot Info:")
        version = ctrl.get_version()
        print(f"   Version: {version}")

        battery = ctrl.get_battery()
        print(f"   Battery: {battery}")
        print()

        # Green LED
        print("🟢 LED: Grün")
        ctrl.set_led(0, 255, 0)
        time.sleep(1)

        # Movement demo
        print("\n📍 Bewegungs-Demo:")

        print("  1. Vorwärts 0.5m")
        ctrl.move_forward(0.5, speed=0.3)
        time.sleep(2)

        print("  2. Stop")
        ctrl.stop()
        time.sleep(0.5)

        print("  3. 90° Drehung")
        ctrl.rotate(90, speed=50)
        time.sleep(2)

        print("  4. Zurück 0.5m")
        ctrl.move_backward(0.5, speed=0.3)
        time.sleep(2)

        print("  5. Züruck zur Startausrichtung")
        ctrl.rotate(-90, speed=50)
        time.sleep(2)

        print("\n🔵 LED: Blau (Fertig)")
        ctrl.set_led(0, 0, 255)
        time.sleep(2)

        # Turn off LEDs
        ctrl.set_led(0, 0, 0)

        print("\n✅ Demo erfolgreich!")

    except KeyboardInterrupt:
        print("\n\n⚠️ Unterbrochen durch Benutzer")
        ctrl.stop()
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        ctrl.stop()
    finally:
        ctrl.close()
        print("\n👋 Verbindung geschlossen")


if __name__ == "__main__":
    demo()
