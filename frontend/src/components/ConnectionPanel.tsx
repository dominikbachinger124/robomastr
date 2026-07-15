import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { connectRobot, disconnectRobot, toRobotState } from "@/lib/api";
import type { RobotState } from "@/types/robot";

interface ConnectionPanelProps {
  /** Called with the updated robot state after a successful connect or disconnect. */
  onRobotStateUpdate?: (state: RobotState) => void;
}

/**
 * Connect / disconnect controls for the robot.
 */
export function ConnectionPanel({ onRobotStateUpdate }: ConnectionPanelProps) {
  const [connType, setConnType] = useState<"ap" | "sta" | "rndis">("ap");
  const [loading, setLoading] = useState(false);
  const [lastError, setLastError] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<string | null>(null);

  const handleConnect = async () => {
    setLoading(true);
    setLastError(null);
    setLastResult(null);
    try {
      const result = await connectRobot(connType);
      setLastResult(
        `Connected via ${result.conn_type ?? connType}${result.sn ? ` (${result.sn})` : ""}`,
      );
      onRobotStateUpdate?.(toRobotState({ connected: true }));
    } catch (error) {
      setLastError(error instanceof Error ? error.message : "Connection failed");
      onRobotStateUpdate?.(toRobotState({ connected: false }));
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = async () => {
    setLoading(true);
    setLastError(null);
    setLastResult(null);
    try {
      await disconnectRobot();
      setLastResult("Disconnected");
      onRobotStateUpdate?.(toRobotState({ connected: false }));
    } catch (error) {
      setLastError(error instanceof Error ? error.message : "Disconnect failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Connection</CardTitle>
        <CardDescription>Choose a mode and connect to the robot.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          {(["ap", "sta", "rndis"] as const).map((mode) => (
            <Button
              key={mode}
              variant={connType === mode ? "default" : "outline"}
              size="sm"
              onClick={() => setConnType(mode)}
              disabled={loading}
            >
              {mode.toUpperCase()}
            </Button>
          ))}
        </div>
        <div className="flex gap-2">
          <Button onClick={handleConnect} disabled={loading}>
            {loading ? "Connecting..." : "Connect"}
          </Button>
          <Button variant="outline" onClick={handleDisconnect} disabled={loading}>
            Disconnect
          </Button>
        </div>
        {lastResult && (
          <p className="text-sm text-green-600 dark:text-green-400">{lastResult}</p>
        )}
        {lastError && (
          <p className="text-sm text-destructive">{lastError}</p>
        )}
      </CardContent>
    </Card>
  );
}
