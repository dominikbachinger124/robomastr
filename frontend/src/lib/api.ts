import type { ConnectionStatus, RobotState } from "@/types/robot";

const ROBOT_API_BASE = "/api/robot";

/** Default telemetry values for fields the bridge /status does not provide. */
export const DEFAULT_ROBOT_STATE: Omit<RobotState, "connected" | "battery_percent" | "wifi_signal_dbm"> = {
  current_speed_mps: 0,
  gimbal_yaw_deg: 0,
  gimbal_pitch_deg: 0,
};

/**
 * Fetch JSON from the backend API.
 *
 * Throws a user-friendly Error on non-2xx responses.
 */
async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    const detail = typeof body?.detail === "string" ? body.detail : response.statusText;
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

/**
 * Connect the backend to the robot bridge / robot.
 */
export async function connectRobot(connType: "ap" | "sta" | "rndis" = "ap"): Promise<ConnectionStatus> {
  return fetchJson<ConnectionStatus>(`${ROBOT_API_BASE}/connect`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ conn_type: connType }),
  });
}

/**
 * Disconnect the robot.
 */
export async function disconnectRobot(): Promise<ConnectionStatus> {
  return fetchJson<ConnectionStatus>(`${ROBOT_API_BASE}/disconnect`, {
    method: "POST",
  });
}

/**
 * Snapshot returned by the robot status endpoint.
 *
 * Mirrors backend/app/api/robot.py::status and the bridge /status response.
 */
export interface RobotStatusResponse {
  /** Whether the robot is connected. */
  connected: boolean;
  /** Battery percentage 0-100, or -1 if unknown. */
  battery_percent?: number;
  /** WiFi signal strength in dBm, or -1 if unknown. */
  wifi_signal_dbm?: number;
}

/**
 * Convert a partial status response into a full RobotState for the dashboard.
 *
 * The bridge /status endpoint only returns a subset of telemetry fields, so
 * defaults are filled in for speed and gimbal angles.
 */
export function toRobotState(status: RobotStatusResponse): RobotState {
  const battery_percent =
    status.battery_percent !== undefined && status.battery_percent >= 0
      ? status.battery_percent
      : 0;
  const wifi_signal_dbm = status.wifi_signal_dbm ?? -1;

  return {
    connected: status.connected,
    battery_percent,
    wifi_signal_dbm,
    ...DEFAULT_ROBOT_STATE,
  };
}

/**
 * Fetch the current robot status from the bridge.
 *
 * Use this to test the full connection chain
 * (frontend → backend → bridge → robot).
 */
export async function getRobotStatus(): Promise<RobotStatusResponse> {
  return fetchJson<RobotStatusResponse>(`${ROBOT_API_BASE}/status`);
}

/**
 * Run the diagnostic LED sequence on gimbal and chassis.
 *
 * The sequence takes about 6.5 seconds. It is a quick way to verify that the
 * robot is connected and responds to SDK commands.
 */
export async function testLed(): Promise<{ status: string }> {
  return fetchJson<{ status: string }>(`${ROBOT_API_BASE}/test-led`, {
    method: "POST",
  });
}

/**
 * Return the URL for the live MJPEG video stream.
 *
 * Points directly at the robot bridge endpoint. Loading it inside an iframe
 * avoids all CORS and proxy issues because the browser renders the stream in
 * its own nested document.
 */
export function getVideoStreamUrl(): string {
  return getBridgeVideoStreamUrl();
}

/**
 * Return the direct MJPEG stream URL on the robot bridge.
 */
export function getBridgeVideoStreamUrl(): string {
  const host = import.meta.env.VITE_BRIDGE_HOST ?? "localhost:8005";
  return `http://${host}/video/stream`;
}

/**
 * Return the backend-proxied MJPEG stream URL.
 */
export function getBackendVideoStreamUrl(): string {
  return "/api/video/stream";
}

/**
 * Return the WebSocket URL for robot control and telemetry.
 */
export function getControlWebSocketUrl(): string {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}${ROBOT_API_BASE}/control`;
}

