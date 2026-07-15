---
description: Create a conventional commit for the dashboard end-to-end milestone
argument-hint: (optional message)
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git add:*), Bash(git commit:*), Bash(git show:*)
---

# Commit: Dashboard End-to-End Milestone

This is a significant milestone: the web dashboard now works end-to-end with the real DJI RoboMaster S1, including gamepad steering, live telemetry, diagnostics, and connection control.

## What changed since the last commit

- `robot-bridge/`: Python 3.8 compatible bridge with HTTP API, SDK wrapper, video stream, LED test, and tests.
- `backend/`: FastAPI app with safety layer, REST proxy, WebSocket control/telemetry, recording stubs, and tests.
- `frontend/`: React 19 dashboard with connection panel, diagnostics, robot status, gamepad input, video feed, and immediate state wiring across REST actions.
- `info.md`: Updated project snapshot documenting fixes and verified end-to-end status.

## Suggested commit message

```text
feat(dashboard): wire frontend state and verify end-to-end robot control

- Share RobotState across Dashboard, ConnectionPanel and DiagnosticsPanel
  for instant UI feedback after connect/disconnect/diagnostics.
- Add getRobotStatus refresh after LED test to reflect real telemetry.
- Fix WebSocket RobotState validation for battery_percent=-1 bridge values.
- Verify end-to-end: connect, telemetry, diagnostics, gamepad steering.

Refs: info.md milestone 13
```

## Steps

1. Review changes:
   !`git status`
   !`git diff HEAD`

2. Stage all relevant files:
   ```bash
   git add info.md commands/commit.md frontend/src/pages/Dashboard.tsx frontend/src/components/ConnectionPanel.tsx frontend/src/components/DiagnosticsPanel.tsx
   ```

3. Create the commit:
   ```bash
   git commit -m "feat(dashboard): wire frontend state and verify end-to-end robot control" -m "- Share RobotState across Dashboard, ConnectionPanel and DiagnosticsPanel" -m "  for instant UI feedback after connect/disconnect/diagnostics." -m "- Add getRobotStatus refresh after LED test to reflect real telemetry." -m "- Fix WebSocket RobotState validation for battery_percent=-1 bridge values." -m "- Verify end-to-end: connect, telemetry, diagnostics, gamepad steering."
   ```

4. Confirm:
   !`git log -1 --stat`

## Notes

- Do not include build artifacts or `node_modules/`.
- If there are unrelated changes in the working tree, stage only the files relevant to this milestone.
