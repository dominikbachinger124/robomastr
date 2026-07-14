"""Thread-safe wrapper around the DJI robomaster SDK."""

from __future__ import annotations

import threading
from typing import Any, Dict

from app.config import Settings
from app.config import settings as _settings
from app.logging import get_logger

logger = get_logger(__name__)

try:
    from robomaster import robot as rm_robot
except ImportError:  # pragma: no cover - allows tests without the SDK
    rm_robot = None


class RobotController:
    """Manages the lifecycle and commands of a single DJI RoboMaster robot.

    This class is the only place in the repository that is allowed to import
    the ``robomaster`` SDK. It runs under Python 3.8 because the SDK is not
    compatible with newer Python versions.

    Use this when you need:
    - Connecting to / disconnecting from the robot
    - Sending chassis, gimbal, or blaster commands
    - Reading high-level robot status

    Do NOT use this class directly from the main backend. Always go through
    the HTTP API exposed by ``app.main``.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize the controller without connecting to a robot."""
        self._settings = settings
        self._robot: Any = None
        self._lock = threading.RLock()
        self._valid_conn_types = {"ap", "sta", "rndis"}

    @property
    def is_connected(self) -> bool:
        """Return True if a robot connection is currently held."""
        with self._lock:
            return self._robot is not None

    def _clamp(self, value: float, max_value: float) -> float:
        return max(-max_value, min(max_value, float(value)))

    def connect(self, conn_type: str | None = None) -> Dict[str, Any]:
        """Connect to the robot using the specified connection type.

        Args:
            conn_type: One of ``ap``, ``sta``, ``rndis``. Defaults to the
                configured ``default_conn_type``.

        Returns:
            A dictionary describing the connection status.

        Raises:
            RuntimeError: If the robomaster SDK is not available.
            ValueError: If ``conn_type`` is not supported.
        """
        conn_type = conn_type or self._settings.default_conn_type

        if conn_type not in self._valid_conn_types:
            raise ValueError(
                f"Invalid conn_type '{conn_type}'. Use one of {self._valid_conn_types}"
            )

        if rm_robot is None:
            raise RuntimeError("robomaster SDK is not installed")

        with self._lock:
            if self._robot is not None:
                logger.info("connect_skipped", reason="already_connected", conn_type=conn_type)
                return {"connected": True, "conn_type": conn_type, "sn": "unknown"}

            logger.info("connect_start", conn_type=conn_type)
            robot = rm_robot.Robot()
            result = robot.initialize(conn_type=conn_type)
            self._robot = robot
            logger.info("connect_complete", conn_type=conn_type, result=result)
            return {
                "connected": True,
                "conn_type": conn_type,
                "sn": str(getattr(robot, "sn", "unknown")),
            }

    def disconnect(self) -> Dict[str, Any]:
        """Disconnect from the robot and release resources."""
        with self._lock:
            if self._robot is None:
                logger.info("disconnect_skipped", reason="not_connected")
                return {"connected": False}

            logger.info("disconnect_start")
            try:
                self._robot.close()
            except Exception as exc:  # pragma: no cover - defensive cleanup
                logger.warning("disconnect_error", error=str(exc))
            finally:
                self._robot = None
            logger.info("disconnect_complete")
            return {"connected": False}

    def move_chassis(self, x: float, y: float, z: float) -> None:
        """Drive the chassis with clamped speeds.

        Args:
            x: Forward/backward speed in m/s.
            y: Left/right speed in m/s.
            z: Rotation speed in °/s.
        """
        x = self._clamp(x, self._settings.max_linear_speed_mps)
        y = self._clamp(y, self._settings.max_linear_speed_mps)
        z = self._clamp(z, self._settings.max_angular_speed_dps)

        with self._lock:
            if self._robot is None:
                raise RuntimeError("Robot is not connected")
            logger.info("chassis_move", x=x, y=y, z=z)
            self._robot.chassis.drive_speed(x=x, y=y, z=z)

    def stop_chassis(self) -> None:
        """Stop chassis movement immediately."""
        with self._lock:
            if self._robot is None:
                raise RuntimeError("Robot is not connected")
            logger.info("chassis_stop")
            self._robot.chassis.drive_speed(x=0.0, y=0.0, z=0.0)

    def move_gimbal(self, pitch_speed: float, yaw_speed: float) -> None:
        """Drive the gimbal with clamped speeds.

        Args:
            pitch_speed: Pitch speed in °/s.
            yaw_speed: Yaw speed in °/s.
        """
        pitch_speed = self._clamp(pitch_speed, self._settings.max_gimbal_speed_dps)
        yaw_speed = self._clamp(yaw_speed, self._settings.max_gimbal_speed_dps)

        with self._lock:
            if self._robot is None:
                raise RuntimeError("Robot is not connected")
            logger.info("gimbal_move", pitch_speed=pitch_speed, yaw_speed=yaw_speed)
            self._robot.gimbal.drive_speed(pitch_speed=pitch_speed, yaw_speed=yaw_speed)

    def stop_gimbal(self) -> None:
        """Stop gimbal movement immediately."""
        with self._lock:
            if self._robot is None:
                raise RuntimeError("Robot is not connected")
            logger.info("gimbal_stop")
            self._robot.gimbal.drive_speed(pitch_speed=0.0, yaw_speed=0.0)

    def fire_blaster(self) -> None:
        """Fire the blaster once."""
        with self._lock:
            if self._robot is None:
                raise RuntimeError("Robot is not connected")
            logger.info("blaster_fire")
            self._robot.blaster.fire()

    def get_status(self) -> Dict[str, Any]:
        """Return a snapshot of the robot status."""
        with self._lock:
            connected = self._robot is not None
            status: Dict[str, Any] = {
                "connected": connected,
                "battery_percent": -1,
                "wifi_signal_dbm": -1,
            }

            if connected:
                try:
                    battery = self._robot.battery.get_battery()
                    status["battery_percent"] = int(battery) if battery is not None else -1
                except Exception as exc:  # pragma: no cover - hardware may not expose it
                    logger.warning("battery_read_error", error=str(exc))

            return status

    def get_camera(self) -> Any:
        """Return the camera module reference."""
        with self._lock:
            if self._robot is None:
                raise RuntimeError("Robot is not connected")
            return self._robot.camera


# Module-level singleton used by the FastAPI app.
robot_controller = RobotController(_settings)
