# RoboMaster S1 SDK Befehlsreferenz

**Schnellstart:** Verbindung über TCP Port 40923, Befehle enden mit `;`

```bash
# Mit netcat verbinden (Direct WiFi)
nc 192.168.2.1 40923

# Oder USB-Modus
nc 192.168.42.2 40923
```

---

## SDK Modus Steuerung

| Befehl | Beschreibung | Antwort |
|--------|--------------|---------|
| `command;` | SDK-Modus aktivieren | `ok` |
| `quit;` | SDK-Modus beenden | `ok` |
| `version ?;` | Firmware-Version | `version 00.00.00.70` |

---

## Roboter-Status

| Befehl | Beschreibung | Beispiel-Antwort |
|--------|--------------|------------------|
| `robot battery ?;` | Batteriestand | `65` (Prozent) |
| `robot mode ?;` | Aktueller Modus | `chassis_lead` |
| `robot mode chassis_lead;` | Chassis-Steuerung | `ok` |
| `robot mode free;` | Freier Modus | `ok` |

---

## Chassis Bewegung (Speed)

**Syntax:** `chassis speed x <vx> y <vy> z <vz>;`

| Befehl | Beschreibung | Parameter |
|--------|--------------|-----------|
| `chassis speed x 0.3;` | Vorwärts mit 0.3 m/s | x: -3.5 bis 3.5 m/s |
| `chassis speed x -0.3;` | Rückwärts | Negativ = Rückwärts |
| `chassis speed y 0.2;` | Seitwärts links | y: -3.5 bis 3.5 m/s |
| `chassis speed z 30;` | Drehen 30°/s | z: -600 bis 600 °/s |
| `chassis speed x 0.3 y 0 z 0;` | Kombiniert | Multi-Achse |
| `chassis speed x 0 y 0 z 0;` | Stop | Alle Achsen 0 |

**AI Sicherheitslimit:** `x` und `y` max 0.5 m/s

---

## Chassis Bewegung (Position)

**Syntax:** `chassis move x <x> y <y> z <z> vxy <v> vz <vz>;`

| Befehl | Beschreibung | Parameter |
|--------|--------------|-----------|
| `chassis move x 1 vxy 0.5;` | 1m vorwärts | x: -5 bis 5 m |
| `chassis move x -1 vxy 0.5;` | 1m rückwärts | Negativ = zurück |
| `chassis move y 0.5 vxy 0.3;` | 0.5m links | y: -5 bis 5 m |
| `chassis move z 90 vz 30;` | 90° drehen | z: -1800 bis 1800° |
| `chassis move x 1 y 0.5 z 45 vxy 0.3 vz 30;` | Kombiniert | Alle Achsen |

---

## Einzel-Rad Steuerung

**Syntax:** `chassis wheel w1 <v> w2 <v> w3 <v> w4 <v>;`

| Befehl | Beschreibung |
|--------|--------------|
| `chassis wheel w1 100 w2 100 w3 100 w4 100;` | Alle vorwärts (RPM) |
| `chassis wheel w1 -100 w2 100 w3 -100 w4 100;` | Drehen vor Ort |
| `chassis wheel w1 0 w2 0 w3 0 w4 0;` | **NOT-STOP** |

**Wertebereich:** -1000 bis 1000 RPM

---

## Gimbal Steuerung

### Gimbal Speed
**Syntax:** `gimbal speed p <pitch> y <yaw>;`

| Befehl | Beschreibung | Parameter |
|--------|--------------|-----------|
| `gimbal speed p 30;` | Nach oben drehen | p: -450 bis 450 °/s |
| `gimbal speed p -30;` | Nach unten drehen | Negativ = unten |
| `gimbal speed y 60;` | Nach rechts drehen | y: -450 bis 450 °/s |
| `gimbal speed y -60;` | Nach links drehen | Negativ = links |
| `gimbal speed p 0 y 0;` | Stop | Beide Achsen 0 |

### Gimbal Position
**Syntax:** `gimbal move p <pitch> y <yaw> vp <vp> vy <vy>;`

| Befehl | Beschreibung | Parameter |
|--------|--------------|-----------|
| `gimbal move p 20 vp 30;` | 20° hoch | p: -55 bis 55° |
| `gassis move p -20 vp 30;` | 20° runter | Negativ = runter |
| `gimbal move y 45 vy 60;` | 45° rechts | y: -360 bis 360° |
| `gimbal move p 0 y 0 vp 30 vy 60;` | Zurück zur Mitte | Beide Achsen |

---

## LED Steuerung

**Syntax:** `led control comp <comp> r <r> g <g> b <b> <effect> <freq>;`

| Befehl | Beschreibung | Parameter |
|--------|--------------|-----------|
| `led control comp all r 255 g 0 b 0;` | Alle LEDs rot | comp: all, top_all, bottom_all |
| `led control comp bottom_all r 0 g 255 b 0;` | Untere LEDs grün | bottom_front, bottom_back |
| `led control comp top_all r 0 g 0 b 255;` | Obere LEDs blau | top_left, top_right |
| `led control comp all r 255 g 255 b 0 flash 5;` | Gelb blinken | flash: 1-10 Hz |
| `led control comp all r 0 g 0 b 255 breath;` | Blau atmen | breath Effekt |
| `led control comp all r 0 g 0 b 0;` | LEDs aus | Schwarz = aus |

**Farben:** r, g, b jeweils 0-255

---

## Blaster (Infrarot)

| Befehl | Beschreibung | Parameter |
|--------|--------------|-----------|
| `blaster fire;` | Einzel-Schuss | Standard |
| `blaster fire count 3;` | 3 Schuss | count: 1-10 |
| `blaster bead ?;` | Verbleibende Munition | Gibt Zahl zurück |

**Hinweis:** Nur wenn Sicherheitsschalter in App deaktiviert!

---

## Sensor Abfragen

| Befehl | Beschreibung | Antwort-Format |
|--------|--------------|----------------|
| `chassis speed ?;` | Aktuelle Geschwindigkeit | `x y z phi` |
| `chassis position ?;` | Position (Odometrie) | `x y z` in m/° |
| `chassis attitude ?;` | Orientierung | `pitch roll yaw` |
| `chassis status ?;` | Status-Flags | `static`/`moving` |
| `gimbal attitude ?;` | Gimbal-Winkel | `pitch yaw roll` |
| `robot battery ?;` | Batterie-Status | `65` oder `charging` |
| `armor event ?;` | Treffer-Events | Event-Code |

---

## Video & Audio Stream

| Befehl | Beschreibung |
|--------|--------------|
| `stream on;` | Video-Stream starten |
| `stream off;` | Video-Stream stoppen |
| `audio on;` | Audio-Stream starten |
| `audio off;` | Audio-Stream stoppen |

---

## Schnell-Beispiele

### Grundbewegung
```bash
command;
chassis move x 0.5 vxy 0.3;
chassis move z 90 vz 30;
chassis move x 0.5 vxy 0.3;
quit;
```

### LED Animation
```bash
command;
led control comp all r 255 g 0 b 0;
led control comp all r 0 g 255 b 0;
led control comp all r 0 g 0 b 255;
led control comp all r 0 g 0 b 0;
quit;
```

### Gimbal Scan
```bash
command;
gimbal move y 45 vy 30;
gimbal move y -45 vy 30;
gimbal move y 0 vy 30;
quit;
```

---

## Wichtige Wertebereiche

| Parameter | Min | Max | Einheit |
|-----------|-----|-----|---------|
| Chassis speed x/y | -3.5 | 3.5 | m/s |
| Chassis speed z | -600 | 600 | °/s |
| Chassis move x/y | -5 | 5 | m |
| Chassis move z | -1800 | 1800 | ° |
| Wheel RPM | -1000 | 1000 | RPM |
| Gimbal speed | -450 | 450 | °/s |
| Gimbal pitch | -55 | 55 | ° |
| Gimbal yaw | -360 | 360 | ° |
| LED RGB | 0 | 255 | - |
| Blaster count | 1 | 10 | Schuss |

---

## Troubleshooting

| Problem | Lösung |
|---------|--------|
| Keine Antwort | `command;` vorher senden |
| `command parse error` | Semikolon `;` vergessen |
| `out of range` | Parameter außerhalb Limits |
| `precondition failed` | Falschem Modus (z.B. `free` statt `chassis_lead`) |
| Keine Bewegung | Batterie prüfen: `robot battery ?;` |
