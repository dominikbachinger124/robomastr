import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { getRobotStatus, testLed, toRobotState } from "@/lib/api";
import type { RobotState } from "@/types/robot";

interface DiagnosticsPanelProps {
  /** Called with the full robot state after a connection or LED test. */
  onRobotStateUpdate?: (state: RobotState) => void;
}

/**
 * Manual diagnostics: test the full connection chain and run the LED sequence.
 */
export function DiagnosticsPanel({
  onRobotStateUpdate,
}: DiagnosticsPanelProps) {
  const [testingConnection, setTestingConnection] = useState(false);
  const [testingLeds, setTestingLeds] = useState(false);
  const [lastResult, setLastResult] = useState<string | null>(null);
  const [lastError, setLastError] = useState<string | null>(null);

  const isBusy = testingConnection || testingLeds;

  const refreshStatus = async () => {
    const status = await getRobotStatus();
    const nextState = toRobotState(status);
    const message = status.connected
      ? `Robot connected (battery ${status.battery_percent ?? "?"}%, WiFi ${status.wifi_signal_dbm ?? "?"} dBm)`
      : "Robot disconnected (bridge is reachable)";
    setLastResult(message);
    onRobotStateUpdate?.(nextState);
  };

  const handleTestConnection = async () => {
    setTestingConnection(true);
    setLastResult(null);
    setLastError(null);
    try {
      await refreshStatus();
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Connection test failed";
      setLastError(message);
      onRobotStateUpdate?.(toRobotState({ connected: false }));
    } finally {
      setTestingConnection(false);
    }
  };

  const handleTestLeds = async () => {
    setTestingLeds(true);
    setLastResult("Running LED sequence...");
    setLastError(null);
    try {
      await testLed();
      setLastResult("LED test completed successfully");
      await refreshStatus();
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "LED test failed";
      setLastError(message);
    } finally {
      setTestingLeds(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Diagnostics</CardTitle>
        <CardDescription>
          Test connection state and hardware features.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap gap-2">
          <Button onClick={handleTestConnection} disabled={isBusy}>
            {testingConnection ? "Testing..." : "Test Connection"}
          </Button>
          <Button
            variant="secondary"
            onClick={handleTestLeds}
            disabled={isBusy}
          >
            {testingLeds ? "Running..." : "Test LEDs"}
          </Button>
        </div>
        {lastResult && (
          <p className="text-sm text-green-600 dark:text-green-400">
            {lastResult}
          </p>
        )}
        {lastError && (
          <p className="text-sm text-destructive">{lastError}</p>
        )}
      </CardContent>
    </Card>
  );
}
