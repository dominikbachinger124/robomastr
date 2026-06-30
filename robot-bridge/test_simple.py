#!/usr/bin/env python3
"""Quick test for RoboMaster S1 connection.

Tests the simple TCP controller.
"""

import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")


def test_usb():
    """Test USB connection (192.168.42.2)."""
    from app.simple_controller import RoboMasterSimpleController

    print("\n" + "=" * 60)
    print("TEST: USB Verbindung (192.168.42.2)")
    print("=" * 60)

    ctrl = RoboMasterSimpleController("192.168.42.2")

    if ctrl.connect():
        print("✅ USB Verbindung erfolgreich!")

        # Test commands
        print("\nTeste Befehle:")

        version = ctrl.get_version()
        print(f"  Version: {version}")

        battery = ctrl.get_battery()
        print(f"  Battery: {battery}")

        print("  LED auf Grün...")
        ctrl.set_led(0, 255, 0)

        ctrl.close()
        print("\n✅ USB Test bestanden!")
        return True
    else:
        print("\n❌ USB Verbindung fehlgeschlagen")
        return False


def test_wifi():
    """Test WiFi connection (192.168.2.1)."""
    from app.simple_controller import RoboMasterSimpleController

    print("\n" + "=" * 60)
    print("TEST: WiFi Verbindung (192.168.2.1)")
    print("=" * 60)

    ctrl = RoboMasterSimpleController("192.168.2.1")

    if ctrl.connect():
        print("✅ WiFi Verbindung erfolgreich!")

        version = ctrl.get_version()
        print(f"  Version: {version}")

        ctrl.close()
        print("\n✅ WiFi Test bestanden!")
        return True
    else:
        print("\n❌ WiFi Verbindung fehlgeschlagen")
        return False


def main():
    print("=" * 60)
    print("🤖 RoboMaster S1 - Verbindungstest")
    print("=" * 60)
    print()
    print("Voraussetzungen:")
    print("  • RoboMaster eingeschaltet")
    print("  • Schalter auf 'Direct Connection'")
    print("  • USB-Kabel verbunden ODER WiFi verbunden")
    print()
    print("WICHTIG: Schalter muss auf Direct Connection stehen!")
    print("         (nicht auf Router Mode)")
    print()

    input("Drücke ENTER wenn bereit...")

    results = {}

    # Test USB
    try:
        results["usb"] = test_usb()
    except Exception as e:
        print(f"\n❌ USB Test Fehler: {e}")
        results["usb"] = False

    # Test WiFi
    try:
        results["wifi"] = test_wifi()
    except Exception as e:
        print(f"\n❌ WiFi Test Fehler: {e}")
        results["wifi"] = False

    # Summary
    print("\n" + "=" * 60)
    print("ZUSAMMENFASSUNG")
    print("=" * 60)

    for name, passed in results.items():
        status = "✅ Funktioniert" if passed else "❌ Fehlgeschlagen"
        print(f"  {name.upper()}: {status}")

    if any(results.values()):
        print("\n🎉 Mindestens eine Verbindung funktioniert!")
        print("\nNutzung:")
        print("  from app.simple_controller import RoboMasterSimpleController")
        print("  ctrl = RoboMasterSimpleController('192.168.42.2')  # oder .2.1")
        print("  ctrl.connect()")
        print("  ctrl.move_forward(1.0)")
        print("  ctrl.close()")
        return 0
    else:
        print("\n⚠️  Keine Verbindung möglich.")
        print("\nPrüfe:")
        print("  1. Ist der Schalter auf 'Direct Connection'?")
        print("  2. Ist der RoboMaster eingeschaltet?")
        print("  3. 10 Sekunden nach dem Einschalten gewartet?")
        print("  4. USB-Kabel in der OBEREN Einheit (Smart Central Control)?")
        return 1


if __name__ == "__main__":
    sys.exit(main())
