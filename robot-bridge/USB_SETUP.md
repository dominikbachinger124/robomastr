# RoboMaster S1 - USB/RNDIS Setup

> **Stabile Verbindung ohne WiFi-Probleme**

## Warum USB?

| WiFi Direct | USB/RNDIS |
|-------------|-----------|
| ❌ Instabil | ✅ Stabil |
| ❌ Latenz | ✅ Geringe Latenz |
| ❌ Störanfällig | ✅ Keine Interferenzen |
| ❌ Reichweitenlimit | ✅ Direkte Verbindung |

## Hardware-Setup

### 1. Kabel anschließen

```
┌─────────────────────────────────────┐
│     Smart Central Control           │
│          (obere Einheit)            │
│                                     │
│  [USB-C Port] ←── Kabel ──→ PC     │
│                                     │
└─────────────────────────────────────┘
```

**Wichtig:** Das Kabel muss in den USB-Port der **oberen Einheit** (Smart Central Control), nicht in den Chassis-USB!

### 2. RoboMaster einschalten

1. RoboMaster einschalten
2. **10 Sekunden warten** (USB-Netzwerk initialisiert sich)
3. Am PC sollte ein neues Netzwerkgerät erscheinen

## Linux Setup

### Automatische Erkennung prüfen

```bash
cd robot-bridge
./setup_usb_linux.sh
```

### Manuelles Setup (falls nötig)

```bash
# 1. USB-Interface finden
ip addr
# → Suche nach "usb", "enx...", "eth..."

# Beispiel-Ausgabe:
# 3: enx123456789abc: <BROADCAST,MULTICAST> mtu 1500 ...

# 2. IP-Adresse zuweisen
sudo ip addr add 192.168.42.20/24 dev enx123456789abc
sudo ip link set enx123456789abc up

# 3. Verbindung testen
ping 192.168.42.2
```

### Mit NetworkManager (GUI)

```bash
# Interface identifizieren
nmcli device

# Automatische Konfiguration
nmcli device modify <INTERFACE> ipv4.method manual ipv4.addresses 192.168.42.20/24
```

## Windows Setup

### 1. Treiber-Installation

1. RoboMaster per USB verbinden
2. Windows erkennt "RNDIS" Gerät
3. Falls keine Treiber gefunden:
   - [Microsoft RNDIS Treiber](https://docs.microsoft.com/en-us/windows-hardware/drivers/network/remote-ndis--rndis-2) verwenden
   - Oder: [USB RNDIS Driver Download](https://www.catalog.update.microsoft.com/Search.aspx?q=remote+ndis)

### 2. Netzwerk-Konfiguration

1. "Netzwerk- und Freigabecenter" öffnen
2. Adaptereinstellungen ändern
3. Neues USB-Ethernet-Gerät finden
4. Eigenschaften → IPv4 → Manuelle Konfiguration:
   - IP: `192.168.42.20`
   - Subnetz: `255.255.255.0`
   - Gateway: `192.168.42.1` (optional)

## Python Controller nutzen

```bash
cd robot-bridge
source .venv/bin/activate

# Demo ausführen
python -m app.usb_controller
```

### Eigener Code

```python
from app.usb_controller import RoboMasterUSBController

ctrl = RoboMasterUSBController()

if ctrl.connect():
    print("Verbunden!")
    
    # Bewegung
    ctrl.move_forward(1.0)  # 1 Meter vorwärts
    ctrl.rotate(90)         # 90° drehen
    
    # LEDs
    ctrl.set_led("bottom_all", 0, 255, 0, "on")
    
    ctrl.disconnect()
```

## Troubleshooting

### "RoboMaster nicht erreichbar"

```bash
# Prüfe ob USB erkannt wird
dmesg | tail -20

# Sollte anzeigen:
# usb 1-1: new high-speed USB device number X using xhci_hcd
# rndis_host 1-1:1.0 usb0: register 'rndis_host'
```

**Lösungen:**
- [ ] Kabel in **obere** Einheit (Smart Central Control)
- [ ] Anderes USB-Kabel probieren
- [ ] USB-Port wechseln (USB 2.0 vs 3.0)
- [ ] RoboMaster neu starten
- [ ] 10+ Sekunden warten nach dem Einschalten

### "No RNDIS device found"

```bash
# Kernel-Module laden
sudo modprobe usbnet
sudo modprobe rndis_host

# Erneut verbinden
```

### Interface verschwindet sofort

**Ursache:** Stromsparmodus oder schlechtes Kabel

**Lösung:**
```bash
# USB-Autosuspend deaktivieren
echo -1 | sudo tee /sys/bus/usb/devices/.../power/autosuspend
```

### Keine Datenverbindung

```bash
# Interface-Statistik prüfen
ip -s addr show <INTERFACE>

# Sollte RX/TX packets zeigen
```

## Technische Details

| Parameter | Wert |
|-----------|------|
| Protokoll | RNDIS (Remote NDIS) |
| RoboMaster IP | `192.168.42.2` |
| Lokale IP | `192.168.42.x` (z.B. `20`) |
| Subnetz | `/24` (255.255.255.0) |
| Port | `40923` (TCP) |
| Geschwindigkeit | USB 2.0 (480 Mbps) |

## Vergleich: USB vs WiFi

| Aspekt | USB | WiFi Direct |
|--------|-----|-------------|
| **Stabilität** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Latenz** | ~1ms | ~5-20ms |
| **Reichweite** | 3m (Kabel) | 30m |
| **Einrichtung** | Einfach | Komplex |
| **Störungen** | Keine | WiFi-Konflikte |
| **Strom** | Via USB | Akku |

**Empfehlung:** USB für Entwicklung, WiFi für autonome Fahrten

## Nächste Schritte

1. ✅ USB-Kabel anschließen
2. ✅ `./setup_usb_linux.sh` ausführen
3. ✅ `python -m app.usb_controller` testen
4. 🚀 Eigene Programme schreiben!

## Support

Falls Probleme auftreten:
1. `dmesg` Ausgabe prüfen
2. `ip addr` Ausgabe prüfen
3. RoboMaster neu starten
4. Anderes USB-Kabel probieren
