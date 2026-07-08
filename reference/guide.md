# RoboMaster S1 – Handlungsfaden (Plaintext-SDK über USB)

> Quelle: RoboMaster Developer Guide
> (https://robomaster-dev.readthedocs.io/zh-cn/latest/)
> Stand: 2026-06-30

## 0. Ausgangslage (bestätigt)
- RoboMaster S1 = **USB Composite Device** (Vorher/Nachher-Test bestätigt):
  - `/dev/ttyACM1` (CDC-ACM, seriell) → liefert ASCII-Telemetrie
  - `enxXXXX` (RNDIS, 192.168.42.2) → Ping ok, SDK-Ports tot
- EP-Python-SDK (`conn_type=rndis/ap`) → `RECV TimeOut!` (S1 öffnet UDP nicht)

## 1. Schlüssel-Erkenntnis aus der Doku
Die Doku enthält ein **明文 SDK (Plaintext-SDK)**:
- `text_sdk/intro.html`       → Einführung
- `text_sdk/connection.html`  → Zugang (WIFI / USB / UART)
- `text_sdk/apis.html`        → Befehlssyntax (`command;`)
- `text_sdk/multi_ctrl.html`  → Formationssteuerung

→ ASCII-Stream auf `ttyACM1` = sehr wahrscheinlich Plaintext-SDK.
→ Befehle enden mit Semikolon `;`, Antworten sind Klartext.

## 2. Voraussetzung: SDK-Modus aktivieren
Das Plaintext-SDK muss EINGESCHALTET werden, sonst keine Steuerung:
1. RoboMaster-App öffnen
2. S1 verbinden
3. SDK-/Lab-Modus aktivieren (ggf. EP-Firmware/Enablement nötig)
4. Erst dann reagiert der Befehlskanal

## 3. Verbindungstest – Schrittfolge

### 3.1 Gerät vorhanden?
    ls -l /dev/ttyACM*

### 3.2 Stream charakterisieren (Text vs. Binär)
    cat /dev/ttyACM1 | xxd | head -40

### 3.3 Plaintext-Handshake senden
Laut Protokoll wird die Verbindung mit `command;` geöffnet:

    python3 - <<'PY'
    import serial, time
    s = serial.Serial('/dev/ttyACM1', 115200, timeout=2)
    def cmd(c):
        s.write((c+';').encode())
        time.sleep(0.3)
        print(c, '->', s.read(200))
    cmd('command')        # SDK-Modus betreten -> erwartet 'ok'
    cmd('version')        # Firmware-Version abfragen
    cmd('robot mode chassis_lead')
    cmd('chassis speed x 0.1 y 0 z 0')   # vorsichtiger Bewegungstest
    cmd('quit')           # SDK-Modus verlassen
    s.close()
    PY

> Baudrate variieren falls keine Antwort: 921600, 230400, 9600.

## 4. Erwartete Antworten
- `command;`  → `ok`   = SDK-Modus aktiv ✅
- `version;`  → z.B. `version 00.00.00.60`
- Keine Antwort / nur Zahlenstrom → SDK-Modus NICHT aktiviert (siehe §2)

## 5. Befehlsreferenz (Auszug Plaintext-Protokoll)
| Zweck | Befehl |
|---|---|
| SDK betreten | `command;` |
| Version | `version;` |
| Steuermodus | `robot mode chassis_lead;` |
| Chassis-Speed | `chassis speed x <v> y <v> z <v>;` |
| Gimbal | `gimbal speed p <v> y <v>;` |
| LED | `led control comp all r <0-255> g <> b <>;` |
| SDK verlassen | `quit;` |

(Vollständig: text_sdk/apis.html)

## 6. Falls ttyACM1 NICHT antwortet
1. Prüfen, ob zweiter Port (`ttyACM0`) der Befehlskanal ist
2. SDK-Modus in App erneut aktivieren (§2)
3. Alternativ WIFI-Direktmodus über Plaintext (`text_sdk/connection.html`)
4. UART-Anbindung prüfen (`extension_module/uart.html`)

## 7. To-Do
- [ ] SDK-Modus in App aktiviert?
- [ ] `command;` liefert `ok`?
- [ ] Bewegungstest erfolgreich?
- [ ] Decoder für Telemetrie-Zahlen (falls separater Stream)
