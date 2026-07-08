# RoboMaster S1 – Verbindungsaufbau & SDK-Fix

**TL;DR:** Ein fehlendes Attribut `DEFAULT_CONN_PROTO = 'udp'` in der `config.py` des RoboMaster-SDK verursachte einen `AttributeError`. Fixe es per `echo`-Befehl (Pfad unten), dann prüfe Netzwerk+Ping VOR dem SDK-Start.

---

## Kontext / Umgebung

- **Projektpfad:** `/home/komodor/robomastr/robot-bridge/robomaster-dev`
- **venv-Pfad:** `/home/komodor/robomastr/robot-bridge/robomaster-dev/.venv/lib/python3.8/site-packages/robomaster`
- **Python:** 3.8, Runner: `uv` (Befehle beginnen mit `uv run python ...`)
- **Drei Verbindungsarten:**
  | Modus   | Beschreibung           | Ziel-IP       |
  |---------|------------------------|---------------|
  | `ap`    | Direct-WLAN (Roboter)  | `192.168.2.1` |
  | `sta`   | Router-Modus           | –             |
  | `rndis` | USB-Kabel              | `192.168.42.2`|

---

## Bekannte Einschränkungen (WICHTIG)

- **Router-Modus (sta)** → NICHT nutzbar: falsches WLAN konfiguriert.
- **Direct-WLAN (ap)** → funktioniert nicht richtig.
- **USB-Connection (rndis)** → macht Probleme (Hardware/Netzwerk).

---

## Problem 1: `AttributeError: DEFAULT_CONN_PROTO`

### Fehlermeldung

```
module 'robomaster.config' has no attribute 'DEFAULT_CONN_PROTO'
```

### Ursache

Das SDK greift in `SdkConnection` auf `config.DEFAULT_CONN_PROTO` zu, aber dieses Attribut fehlt in der installierten `config.py`-Version.

Die Analyse in `conn.py` zeigt:

```python
class Connection(BaseConnection):
    def __init__(self, host_addr, target_addr, proto="v1", protocol=CONNECTION_PROTO_UDP):
```

In `BaseConnection.create()` werden nur `'tcp'` oder `'udp'` korrekt behandelt:

```python
if self._proto_type == CONNECTION_PROTO_TCP:   # 'tcp'
    ...
elif self._proto_type == CONNECTION_PROTO_UDP: # 'udp'
    ...
else:
    logger.error("Connection: {0} unexpected connection param set")
```

**Der Wert muss `'udp'` sein (NICHT `'ap'`).**

### Lösung (angewendet)

**Neue Zeile anhängen:**

```bash
echo "DEFAULT_CONN_PROTO = 'udp'" >> /home/komodor/robomastr/robot-bridge/robomaster-dev/.venv/lib/python3.8/site-packages/robomaster/config.py
```

**Falls die Variable bereits existiert – ersetzen statt anhängen:**

```bash
sed -i "s/^DEFAULT_CONN_PROTO\s*=.*/DEFAULT_CONN_PROTO = 'udp'/" /home/komodor/robomastr/robot-bridge/robomaster-dev/.venv/lib/python3.8/site-packages/robomaster/config.py
```

**Verifikation:**

```bash
uv run python -c "from robomaster import config; print(config.DEFAULT_CONN_PROTO)"
```

Erwartete Ausgabe:

```
udp
```

✅ **Status: BEHOBEN.**

---

## Problem 2: `RECV TimeOut!` (Netzwerk / Hardware – unabhängig von Problem 1)

### Fehlermeldungen

```
# ap-Modus:
SdkConnection: RECV TimeOut!
Connection Failed ... conn_type ap, host ('0.0.0.0', 10262), target ('192.168.2.1', 20020)

# rndis-Modus:
Connection Failed ... conn_type rndis, host ('192.168.42.3', 10175), target ('192.168.42.2', 20020)
```

### Ursache

In `SdkConnection.switch_remote_route` wird eine initiale UDP-Anfrage an den Proxy-Port des Roboters gesendet. Keine Antwort → `RECV TimeOut!`. Das ist ein **physisches Netzwerk-/Hardwareproblem**, unabhängig vom `config`-Fix.

### Diagnose-Schritte (Reihenfolge einhalten!)

**1. Verbindungsart wählen:**
   - `rndis` (USB) → Ziel-IP `192.168.42.2`
   - `ap` (Direct-WLAN) → Ziel-IP `192.168.2.1`

**2. Hardware prüfen:**
   - Roboter eingeschaltet?
   - Physischer Connection-Schalter am Intelligent Controller auf den passenden Modus (USB-Symbol für `rndis`)?
   - USB-Kabel direkt am Controller eingesteckt?

**3. Netzwerk-Interface prüfen (USB/rndis):**

```bash
ip addr
```

Suche ein Interface mit IP im Bereich `192.168.42.x` (z.B. `192.168.42.3`).

**4. Roboter anpingen:**

```bash
# USB:
ping -c 4 192.168.42.2

# AP-WLAN:
ping -c 4 192.168.2.1
```

| Ergebnis    | Bedeutung                        | Nächster Schritt             |
|-------------|----------------------------------|------------------------------|
| ✅ Antwort  | Netzwerk steht                   | SDK-Script starten           |
| ❌ Timeout   | Hardware-/Treiberproblem         | Treiber / Kabel / Schalter   |

**5. Erst bei erfolgreichem Ping SDK-Script starten:**

```bash
# USB:
uv run python text2.py

# AP-WLAN:
uv run python text.py
```

### Weitere Hinweise bei hartnäckigem `RECV TimeOut`

- Firewall prüfen (UDP-Port `20020` freigeben)
- Lokale Bind-Adresse explizit setzen
- Roboter-Modus (Mode A/B/C) prüfen
- Roboter neustarten und venv neu starten

---

## Relevante Ports & Adressen (aus SDK)

| Feld               | Wert              |
|--------------------|-------------------|
| Robot Device Port  | `20020` (Ziel)    |
| Proxy-Port         | Initial Route-Switch (UDP) |
| ap: target         | `192.168.2.1`     |
| ap: local host     | `0.0.0.0`         |
| rndis: target      | `192.168.42.2`    |
| rndis: local       | `192.168.42.3`    |

---

## Empfohlene Reihenfolge für den Agenten-Harness

```
1. config-Fix sicherstellen (Problem 1)
   → Verifikation: uv run python -c "from robomaster import config; print(config.DEFAULT_CONN_PROTO)"
   
2. Physische Verbindung über ping verifizieren
   → PING VOR jedem SDK-Script – sonst unnötige Fehlerdiagnose
   
3. Bei RECV TimeOut trotz erfolgreichem Ping:
   → Firewall / lokale Bind-Adresse / Roboter-Modus prüfen
   
4. Verbindungstyp passend zum physischen Setup wählen:
   → rndis für USB, ap für Direct-WLAN
```

---

*Erstellt auf Basis der Diagnosesitzung: Robomaster S1 SDK Connection Troubleshooting, Juni 2026.*
