# RoboMasterPy — Python SDK für RoboMaster S1/EP

> Community-Python-SDK für DJI RoboMaster
> Quelle: https://github.com/nanmu42/robomasterpy
> Doku: https://robomasterpy.nanmu.me/en/latest/

## ⚠️ Sicherheitshinweise
- Roboter kann Menschen/Tiere verletzen, Dinge oder sich selbst beschädigen.
- Genug Platz sicherstellen, Boden freihalten.
- Langsam starten, keine hohen Geschwindigkeiten beim Debuggen.
- Polster verwenden.

## Installation

```bash
pip install robomasterpy opencv-contrib-python
```

Für Python 3.6 zusätzlich:
```bash
pip install dataclasses
```

## Schnellstart

```python
import robomasterpy as rm

# Verbinden (IP je nach Modus)
cmd = rm.Commander(ip="192.168.42.2")  # USB-Modus

# Basisbewegung
cmd.robot_mode(rm.MODE_CHASSIS_LEAD)
cmd.chassis_speed(x=0.3)  # Vorwärts 0.3 m/s
time.sleep(1)
cmd.chassis_speed(x=0)    # Stopp

# Aufräumen
cmd.close()
```

## Verbindungsmodi

| Modus | IP-Adresse | Beschreibung |
|-------|------------|--------------|
| USB | `192.168.42.2` | Kabelverbindung (stabilst) |
| Direkt-WiFi | `192.168.2.1` | Mit Roboter-WLAN verbinden |
| Router | `""` (auto) | Im selben Netzwerk |

## Wichtige Dateien

- `examples/robomasterpy_basic.py` - Einfacher Verbindungstest
- `examples/robomasterpy_simple_controller.py` - Wiederverwendbare Controller-Klasse
- `reference/robomasterpy_guide.md` - Vollständige API-Referenz

## Voraussetzungen

- RoboMaster S1: Gerootete Firmware für externen SDK-Zugriff
- RoboMaster EP: Funktioniert out-of-the-box
- SDK-Modus in RoboMaster-App aktivieren
