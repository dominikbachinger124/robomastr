import { useCallback, useState } from "react";
import { Button } from "@/components/ui/button";
import { ConnectionPanel } from "@/components/ConnectionPanel";
import { DiagnosticsPanel } from "@/components/DiagnosticsPanel";
import { GamepadPanel } from "@/components/GamepadPanel";
import { RobotStatus } from "@/components/RobotStatus";
import { VideoFeed } from "@/components/VideoFeed";
import { useWebSocket } from "@/hooks/useWebSocket";
import type { GamepadAxes, GamepadButtons, RobotState, WebSocketMessage } from "@/types/robot";

interface DashboardState {
  robotState: RobotState | null;
  lastError: string | null;
}

/**
 * Main robot control dashboard.
 *
 * Combines connection controls, live telemetry, video feed, and gamepad input.
 */
export function Dashboard() {
  const [state, setState] = useState<DashboardState>({
    robotState: null,
    lastError: null,
  });
  const [videoActive, setVideoActive] = useState(false);

  const handleRobotState = useCallback(
    (message: WebSocketMessage & { type: "robot_state" }) => {
      setState((prev) => ({ ...prev, robotState: message.state, lastError: null }));
    },
    [],
  );

  const handleError = useCallback(
    (message: WebSocketMessage & { type: "error" }) => {
      setState((prev) => ({ ...prev, lastError: message.message }));
    },
    [],
  );

  const { isConnected, sendGamepadState, sendCommand } = useWebSocket({
    onRobotState: handleRobotState,
    onError: handleError,
  });

  const handleGamepadState = useCallback(
    (axes: GamepadAxes, buttons: GamepadButtons) => {
      sendGamepadState(axes, buttons);
    },
    [sendGamepadState],
  );

  const handleRobotStateUpdate = useCallback((nextState: RobotState) => {
    setState((prev) => ({ ...prev, robotState: nextState, lastError: null }));
  }, []);

  return (
    <div className="min-h-screen p-6">
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Robomastr</h1>
          <p className="text-sm text-muted-foreground">
            AI Agent control dashboard for DJI RoboMaster S1
          </p>
        </div>
        <Button
          variant={videoActive ? "default" : "outline"}
          onClick={() => setVideoActive((prev) => !prev)}
        >
          {videoActive ? "Pause Video" : "Start Video"}
        </Button>
      </header>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-1">
          <ConnectionPanel onRobotStateUpdate={handleRobotStateUpdate} />
          <DiagnosticsPanel onRobotStateUpdate={handleRobotStateUpdate} />
          <RobotStatus state={state.robotState} wsConnected={isConnected} />
          <GamepadPanel onState={handleGamepadState} />
          <div className="flex gap-2">
            <Button
              variant="destructive"
              className="flex-1"
              onClick={() => sendCommand("stop", `stop-${Date.now()}`)}
            >
              Emergency Stop
            </Button>
            <Button
              variant="secondary"
              onClick={() => sendCommand("fire", `fire-${Date.now()}`)}
            >
              Fire
            </Button>
          </div>
          {state.lastError && (
            <p className="text-sm text-destructive">{state.lastError}</p>
          )}
        </div>

        <div className="lg:col-span-2">
          <VideoFeed active={videoActive} />
        </div>
      </div>
    </div>
  );
}
