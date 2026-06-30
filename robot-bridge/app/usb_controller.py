"""RoboMaster S1 USB/RNDIS Controller.

Für stabile USB-Verbindung ohne WiFi-Probleme.

Setup:
1. USB-Kabel vom PC in den USB-Port des Smart Central Control (obere Einheit)
2. Der RoboMaster wird als Netzwerkkarte (RNDIS) erkannt
3. Diesen Controller nutzen

Vorteile gegenüber WiFi:
- Keine Verbindungsabbrüche
- Geringere Latenz
- Keine Interferenzen
- Stromversorgung möglich (je nach Port)

Netzwerk-Konfiguration:
- RoboMaster IP: 192.168.42.2
- Lokale IP: 192.168.42.x (automatisch oder manuell)
"""

from __future__ import annotations

import logging
import subprocess
import sys
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from robomaster.robot import Robot
    from robomaster.chassis import Chassis
    from robomaster.gimbal import Gimbal
    from robomaster.led import Led

from robomaster import robot
from robomaster import config

logger = logging.getLogger(__name__)


class RoboMasterUSBController:
    """RoboMaster S1 Controller für USB/RNDIS Verbindung.

    Nutzt USB-Kabel direkt am Smart Central Control für stabile Verbindung.

    Example:
        >>> ctrl = RoboMasterUSBController()
        >>> if ctrl.connect():
        ...     ctrl.move_forward(1.0)
        ...     ctrl.disconnect()
    """

    # USB/RNDIS Default Settings
    ROBOT_IP = "192.168.42.2"
    LOCAL_IP = "192.168.42.20"  # Static IP for PC

    def __init__(self, local_ip: str = LOCAL_IP) -> None:
        """Initialize USB controller.

        Args:
            local_ip: Lokale IP-Adresse für den PC (im 192.168.42.x Netz)
        """
        self._robot: Robot | None = None
        self._chassis: Chassis | None = None
        self._gimbal: Gimbal | None = None
        self._led: Led | None = None
        self._is_connected = False
        self._local_ip = local_ip

    def _check_usb_connection(self) -> bool:
        """Überprüfe ob USB-Verbindung verfügbar ist.

        Returns:
            True wenn RoboMaster USB-Netzwerk erreichbar
        """
        try:
            # Ping test to robot
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "2", self.ROBOT_IP],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    def connect(self) -> bool:
        """Verbinde via USB/RNDIS.

        Returns:
            True bei erfolgreicher Verbindung
        """
        try:
            print(f"🔌 Prüfe USB-Verbindung zu {self.ROBOT_IP}...")

            if not self._check_usb_connection():
                print("❌ RoboMaster nicht erreichbar!")
                print("   1. Ist das USB-Kabel angeschlossen?")
                print("   2. Ist der RoboMaster eingeschaltet?")
                print("   3. Warte 10 Sekunden nach dem Einschalten")
                return False

            print(f"✅ USB-Netzwerk erkannt")
            print(f"📝 Setze lokale IP: {self._local_ip}")

            # Set local IP for RNDIS connection
            config.LOCAL_IP_STR = self._local_ip

            print(f"🔗 Verbinde mit RoboMaster...")
            self._robot = robot.Robot()

            # conn_type='rndis' für USB-Verbindung
            self._robot.initialize(conn_type="rndis")

            self._chassis = self._robot.chassis
            self._gimbal = self._robot.gimbal
            self._led = self._robot.led

            self._is_connected = True

            # Get robot info
            version = self._robot.get_version()
            sn = self._robot.get_sn()
            battery = self._robot.battery.get_battery()

            print(f"✅ Verbunden!")
            print(f"   Version: {version}")
            print(f"   SN: {sn}")
            print(f"   🔋 Batterie: {battery}%")

            logger.info(
                f"USB Connected - Version: {version}, SN: {sn}, Battery: {battery}%"
            )
            return True

        except Exception as e:
            logger.error(f"USB Connection failed: {e}")
            print(f"❌ Verbindung fehlgeschlagen: {e}")
            print("\nTroubleshooting:")
            print("  • Linux: Prüfe 'dmesg | grep rndis' oder 'ip addr'")
            print("  • Windows: Treiber im Gerätemanager prüfen")
            print("  • RoboMaster neu starten und 10 Sekunden warten")
            self._is_connected = False
            return False

    def disconnect(self) -> None:
        """USB-Verbindung trennen."""
        if self._robot:
            try:
                self._robot.close()
                print("🔌 Verbindung getrennt")
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
        """Bewegung ausführen.

        Args:
            x: Vorwärts/Rückwärts in Metern (-5 bis 5)
            y: Links/Rechts in Metern (-5 bis 5)
            z: Rotation in Grad (-1800 bis 1800)
            xy_speed: Geschwindigkeit m/s (0.5-2.0, AI: max 0.5)
            z_speed: Rotationsgeschwindigkeit deg/s (10-540)
        """
        if not self._chassis:
            raise RuntimeError("Nicht verbunden")

        action = self._chassis.move(x=x, y=y, z=z, xy_speed=xy_speed, z_speed=z_speed)
        action.wait_for_completed()
        logger.debug(f"Move: x={x}, y={y}, z={z}")

    def move_forward(self, distance: float, speed: float = 0.5) -> None:
        """Vorwärts bewegen.

        Args:
            distance: Distanz in Metern (positiv = vorwärts)
            speed: Geschwindigkeit m/s (max 0.5 für AI)
        """
        self.move(x=distance, xy_speed=speed)

    def move_backward(self, distance: float, speed: float = 0.5) -> None:
        """Rückwärts bewegen."""
        self.move(x=-distance, xy_speed=speed)

    def rotate(self, degrees: float, speed: int = 100) -> None:
        """Drehen.

        Args:
            degrees: Grad (positiv = rechts/Uhrzeigersinn)
            speed: Geschwindigkeit deg/s (10-540)
        """
        self.move(z=degrees, z_speed=speed)

    def stop(self) -> None:
        """Notstopp - sofort anhalten."""
        if self._chassis:
            self._chassis.drive_speed(x=0, y=0, z=0)
            logger.debug("Emergency stop")

    def set_led(
        self, component: str, r: int, g: int, b: int, effect: str = "on"
    ) -> None:
        """LED-Farbe setzen.

        Args:
            component: "all", "top_all", "bottom_all", "bottom_front", etc.
            r, g, b: RGB Werte 0-255
            effect: "on", "off", "flash", "breath"
        """
        if not self._led:
            raise RuntimeError("Nicht verbunden")
        self._led.set_led(comp=component, r=r, g=g, b=b, effect=effect)

    def turn_off_leds(self) -> None:
        """Alle LEDs ausschalten."""
        if self._led:
            self._led.set_led(comp="all", r=0, g=0, b=0, effect="off")

    def get_battery(self) -> int:
        """Batteriestand abfragen.

        Returns:
            Batterielevel 0-100, oder -1 bei Fehler
        """
        if self._robot:
            try:
                return self._robot.battery.get_battery()
            except Exception as e:
                logger.error(f"Battery check failed: {e}")
        return -1

    def get_position(self) -> tuple:
        """Aktuelle Position abfragen.

        Returns:
            (x, y, z) Position in Metern/Grad
        """
        if self._robot and self._chassis:
            try:
                position = self._chassis.get_position()
                return position
            except Exception as e:
                logger.error(f"Position check failed: {e}")
        return (0.0, 0.0, 0.0)


def demo_usb_connection():
    """Demo für USB-Verbindung.

    Voraussetzungen:
    1. USB-Kabel in Smart Central Control (oben am RoboMaster)
    2. RoboMaster eingeschaltet
    3. 10 Sekunden warten bis USB-Netzwerk bereit
    """
    print("=" * 60)
    print("🤖 RoboMaster S1 - USB/RNDIS Demo")
    print("=" * 60)
    print()
    print("Voraussetzungen:")
    print("  1. USB-Kabel in Smart Central Control (obere Einheit)")
    print("  2. RoboMaster eingeschaltet")
    print("  3. 10 Sekunden gewartet")
    print()

    ctrl = RoboMasterUSBController()

    print("Verbinde via USB...")
    if not ctrl.connect():
        print("\n❌ Verbindung fehlgeschlagen!")
        return

    try:
        # Grün = Bereit
        ctrl.set_led("bottom_all", 0, 255, 0, "on")
        print("\n🟢 LED: Grün (Bereit)")

        # Bewegungs-Demo
        print("\n📋 Demo-Sequenz:")

        print("  1. Vorwärts 0.5m")
        ctrl.move_forward(0.5, speed=0.3)
        time.sleep(0.5)

        print("  2. 90° Drehung")
        ctrl.rotate(90, speed=50)
        time.sleep(0.5)

        print("  3. Vorwärts 0.5m")
        ctrl.move_forward(0.5, speed=0.3)
        time.sleep(0.5)

        print("  4. 90° Drehung")
        ctrl.rotate(90, speed=50)
        time.sleep(0.5)

        print("  5. Zurück zur Startposition")
        ctrl.move_forward(-0.5, speed=0.3)
        ctrl.rotate(-180, speed=50)
        ctrl.move_forward(-0.5, speed=0.3)

        # Blau = Fertig
        ctrl.set_led("bottom_all", 0, 0, 255, "breath")
        print("\n🔵 LED: Blau (Demo abgeschlossen)")
        print("✅ Demo erfolgreich!")

        # Batterie-Check
        battery = ctrl.get_battery()
        print(f"\n🔋 Aktueller Batteriestand: {battery}%")

    except KeyboardInterrupt:
        print("\n⚠️ Demo unterbrochen durch Benutzer")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
    finally:
        ctrl.turn_off_leds()
        ctrl.disconnect()
        print("\n👋 Auf Wiedersehen!")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    demo_usb_connection()
