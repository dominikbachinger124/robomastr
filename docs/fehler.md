# Archon Workflow Fehlerprotokoll

> Erstellt: 2026-07-14
> Workflow: `archon-plan-to-pr`
> Ausgelöst von: Manuelle Interaktion mit Archon zur Prüfung der Pläne

---

## 1. Ausgeführter Befehl

```bash
archon workflow run plan-to-pr --cwd . --plan plans/01-robot-bridge.md --dry-run
```

**Arbeitsverzeichnis:** `/home/komodor/robomastr`
**Plan-Datei:** `plans/01-robot-bridge.md`

---

## 2. Beobachtetes Verhalten

### 2.1 Workflow-Initialisierung (erfolgreich)

Archon hat den Workflow korrekt erkannt und gestartet:

- Workflow-Name: `archon-plan-to-pr`
- Provider: `pi` / `mammouth` / Modell: `claude-opus-4-5`
- Branch/Worktree wurde erstellt: `plan-to-pr-1784016479823`
- Worktree-Pfad: `/home/komodor/.archon/workspaces/komodor/robomastr/worktrees/archon/task-plan-to-pr-1784016479823`

Log-Auszug:
```json
{"level":30,"time":1784016480984,"pid":109966,"module":"workflow.executor","workflowName":"archon-plan-to-pr","provider":"pi","providerSource":"config","model":"mammouth/claude-opus-4-5","msg":"workflow_provider_resolved"}
```

---

### 2.2 Kritische Fehler

#### Fehler 1: OpenAI API Rate-Limit (blockierend)

```
OpenAI API error (429): 429 Rate limit exceeded for api_key: 2bd2534c31a307679f3e98724d5fe54d8d1a8a388d4df8c8c5f13d8a949638fe.
Limit type: tokens.
Current limit: 100000,
Remaining: 0.
Limit resets at: 2026-07-14 08:09:35 UTC
```

- **Auswirkung:** Der erste DAG-Knoten `plan-setup` ist gescheitert.
- **Importanz:** Blockierend. Ohne erfolgreiche API-Antwort kann der Workflow nicht fortfahren.
- **Reset-Zeit:** 2026-07-14 08:09:35 UTC

#### Fehler 2: Tool-Ausführungsfehler innerhalb des Workflows

Während des `plan-setup`-Knotens wurden mehrere Warnungen protokolliert:

```
⚠️ Tool read failed
⚠️ Tool bash failed
```

- **Kontext:** Diese Warnungen traten auf, bevor der Rate-Limit-Fehler den Knoten beendete.
- **Mögliche Ursachen:**
  - Der Agent im Workflow-Knoten konnte nicht auf die erwarteten Tools zugreifen (Read/Bash).
  - Eventuell fehlende Berechtigungen im temporären Worktree.
  - Provider/Konfigurationsproblem bei `mammouth` (siehe Fehler 3).

#### Fehler 3: Provider-Konfiguration unvollständig

```
Provider 'mammouth' is not in the Archon adapter's env-var table — file an issue if you want a shortcut env var for it.
Or run `pi` and type `/login` locally to authenticate 'mammouth' via OAuth;
credentials land in ~/.pi/agent/auth.json and are picked up automatically.
```

- **Beobachtung:** Archon hat den Workflow trotzdem mit `mammouth/claude-opus-4-5` gestartet, aber meldete diese Auth-Hinweise mehrfach.
- **Mögliche Ursache:** Der Provider wurde über eine Konfigurationsdatei ausgewählt, aber die Auth-Methode (OAuth/Token) ist nicht korrekt hinterlegt.

---

## 3. Workflow-Status

- **Workflow:** `archon-plan-to-pr`
- **Ergebnis:** Abgebrochen
- **Letzter erfolgreicher Knoten:** Keiner (nur Initialisierung)
- **Fehlgeschlagener Knoten:** `plan-setup`
- **Retries:** 1/3 durchgeführt, dann Timeout (`SIGTERM` nach 120s)

---

## 4. Offene Fragen für Archon-Support

Bei Rückfrage an Archon/Mammouth Support sollten folgende Punkte geklärt werden:

1. **Rate-Limiting**
   - Warum wurde das Token-Limit von 100.000 sofort auf 0 gesetzt?
   - Gibt es eine Möglichkeit, auf ein anderes Modell mit höherem Limit zu wechseln?
   - Ist das Limit pro Stunde/Tag oder pro Anfrage?

2. **Provider-Auth `mammouth`**
   - Wird `mammouth` offiziell unterstützt?
   - Welche Umgebungsvariablen oder Konfigurationsdateien sind nötig?
   - Was bedeutet der Hinweis auf `~/.pi/agent/auth.json` konkret?

3. **Tool-Fehler im Worktree**
   - Warum schlagen `Tool read failed` und `Tool bash failed` im Worktree fehl?
   - Handelt es sich um ein Berechtigungsproblem oder ein Konfigurationsproblem?
   - Ist der Worktree-Pfad relevant (`/home/komodor/.archon/workspaces/...`)?

4. **Plan-Datei-Standort**
   - Akzeptiert `archon-plan-to-pr` Pläne nur aus `$ARTIFACTS_DIR` oder `.agents/plans/`?
   - Ist die Übergabe via `--plan plans/01-robot-bridge.md` korrekt?

5. **Dry-Run-Verhalten**
   - Wird bei `--dry-run` tatsächlich kein Code geändert?
   - Warum wurde trotz `--dry-run` ein Worktree/Branch erstellt?

---

## 5. Empfohlene Nächste Schritte

1. **Rate-Limit abwarten oder API-Key/Modell wechseln**
   - Nach Reset-Zeit erneut versuchen.
   - Alternatives Modell mit höherem Limit verwenden (z. B. gpt-4o-mini, claude-3-5-sonnet).

2. **Provider-Auth prüfen**
   - `pi` starten und `/login` ausführen, falls `mammouth` OAuth benötigt.
   - Oder ARCHON_API_KEY / passende Env-Variable setzen.

3. **Einfacheren Workflow testen**
   - Vor dem erneuten `plan-to-pr`-Versuch einen kleinen Workflow wie `archon-assist` oder `archon-test-loop-dag` ausführen, um Tooling und Auth zu validieren.

4. **Alternative: Manuelle Implementierung**
   - Die Pläne in `plans/01-robot-bridge.md`, `plans/02-backend-api.md`, `plans/03-frontend-ui.md`, `plans/04-integration-and-recording.md` sind detailliert genug, um ohne Archon-Workflow ausgeführt zu werden.

---

## 6. Anhang: Vollständige Pläne

Die betroffenen Plan-Dateien liegen unter:

- `plans/01-robot-bridge.md`
- `plans/02-backend-api.md`
- `plans/03-frontend-ui.md`
- `plans/04-integration-and-recording.md`

Zusätzlich existiert der ursprüngliche monolithische Plan:

- `plans/s1-web-control-interface.md`

---

*Diese Datei dient als Referenz für eine spätere Klärung mit Archon/Mammouth Support.*
