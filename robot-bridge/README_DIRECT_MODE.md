# RoboMaster S1 Control - Ohne DJI App

> Die RoboMaster S1 App wurde 2020 eingestellt. Diese Lösungen funktionieren **ohne App**!

## Schnellstart

### 1. Direct Connection Mode (Empfohlen)

**Hardware-Setup:**
1. RoboMaster S1 einschalten
2. Schalter am Smart Central Control auf **"Direct Connection"** stellen (nicht Router Mode)
3. Am PC: Mit WiFi-Netzwerk `RoboMaster_S1_XXXXXX` verbinden
4. Kein Passwort nötig (oder Standard-Passwort prüfen)

**IP-Adressen:**
- RoboMaster: `192.168.2.1`
- Dein PC bekommt: `192.168.2.x`

### 2. Python Controller nutzen

```bash
cd robot-bridge
source .venv/bin/activate

# Demo ausführen
python -m app.direct_controller
```

### 3. Web-Interface (Einfachste Steuerung)

```bash
cd robot-bridge
source .venv/bin/activate
python web_interface.py
```

Dann im Browser öffnen: **http://localhost:8000**

## Verbindungsmethoden

### A. Direct Connection (WiFi)

```python
from app.direct_controller import RoboMasterDirectController

ctrl = RoboMasterDirectController()
ctrl.connect()  # Verbindet mit 192.168.2.1

# Bewegen
ctrl.move_forward(1.0)  # 1 Meter vorwärts
ctrl.rotate(90)         # 90° drehen

# LEDs
ctrl.set_led("bottom_all", 0, 255, 0, "on")  # Grün
ctrl.turn_off_leds()

ctrl.disconnect()
```

### B. USB-Verbindung (RNDIS)

**Vorteile:** Sehr stabil, keine WiFi-Probleme

1. USB-Kabel vom PC in den USB-Port des Smart Central Control
2. RoboMaster wird als Netzwerkkarte erkannt
3. IP: `192.168.42.2`

```python
from robomaster import robot, config

config.LOCAL_IP_STR = "192.168.42.20"
ep_robot = robot.Robot()
ep_robot.initialize(conn_type='rndis')  # USB statt WiFi

# Dein Code...
ep_robot.close()
```

## Troubleshooting

### "Connection failed"

**Prüfen:**
- [ ] Schalter steht auf "Direct Connection" (nicht Router)
- [ ] PC ist mit RoboMaster WiFi verbunden
- [ ] RoboMaster ist eingeschaltet (Akku > 20%)

### "No route to host"

```bash
# IP-Adresse prüfen
ping 192.168.2.1

# Alternative: Manuelle IP setzen
python -c "from app.direct_controller import RoboMasterDirectController; 
ctrl = RoboMasterDirectController('192.168.2.1'); 
ctrl.connect()"
```

### Router Mode (nicht empfohlen ohne App)

> ⚠️ **Warnung:** Ohne funktionierende App kannst du das Router-WiFi nicht mehr ändern!

Falls der RoboMaster bereits in einem Router-Netzwerk konfiguriert ist:
1. Schalter auf Router Mode stellen
2. PC mit selbem Netzwerk verbinden
3. IP im Code anpassen (z.B. `192.168.1.100`)

## Features

| Feature | Direct Ctrl | Web Interface |
|---------|-------------|---------------|
| Verbindung | ✅ | ✅ |
| Bewegung | ✅ | ✅ |
| Drehung | ✅ | ✅ |
| LEDs | ✅ | ✅ |
| Batterie | ✅ | ✅ |
| Kamera | ❌ | ❌ |
| Blaster | ⚠️ Manuell | ❌ |

## Unterschiede zur alten App

| Funktion | Alte App | Diese Lösung |
|----------|----------|--------------|
| Verfügbarkeit | ❌ Eingestellt | ✅ Funktioniert |
| Router wechseln | ✅ | ❌ (nur Direct Mode) |
| FPV Video | ✅ | ❌ |
| Scratch/Python | ✅ | ✅ (echtes Python) |
| Live-Steuerung | ✅ | ✅ (Web Interface) |

## Bekannte Einschränkungen

1. **Router-Modus:** Ohne App kann das WiFi-Netzwerk nicht geändert werden
2. **FPV Video:** Kein Live-Video-Stream verfügbar
3. **Firmware-Updates:** Nicht möglich ohne App
4. **Scratch:** Nicht verfügbar (aber echtes Python ist besser!)

## Dateien

```
robot-bridge/
├── app/
│   ├── robot.py              # Basis Controller
│   └── direct_controller.py  # Direct Connection (empfohlen)
├── examples/
│   └── usb_connection.py     # USB/RNDIS Beispiel
├── web_interface.py          # Web-Interface
└── test_robot.py             # Tests
```

## Weiterentwicklung

- [ ] Kamera-Stream via OpenCV
- [ ] Blaster-Steuerung
- [ ] Automatische Fahrt-Programme
- [ ] KI-Integration (Objekterkennung)

## Links

- [RoboMaster SDK Docs](https://robomaster-dev.readthedocs.io/)
- [GitHub SDK](https://github.com/dji-sdk/RoboMaster-SDK)
