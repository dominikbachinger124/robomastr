"""FastAPI application for the RoboMastr robot bridge."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict

from fastapi import FastAPI, HTTPException
from fastapi import status as http_status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, field_validator

from app.config import settings
from app.logging import get_logger
from app.robot import robot_controller
from app.video import VideoStreamer

logger = get_logger(__name__)


class ConnectRequest(BaseModel):
    """Connection request body."""

    conn_type: str = Field(default=settings.default_conn_type, description="ap, sta, or rndis")

    @field_validator("conn_type")
    @classmethod
    def _validate_conn_type(cls, value: str) -> str:
        if value not in {"ap", "sta", "rndis"}:
            raise ValueError("conn_type must be one of: ap, sta, rndis")
        return value


class ChassisMoveRequest(BaseModel):
    """Chassis speed request body."""

    x: float = Field(default=0.0, description="Forward/backward speed in m/s")
    y: float = Field(default=0.0, description="Left/right speed in m/s")
    z: float = Field(default=0.0, description="Rotation speed in °/s")


class GimbalMoveRequest(BaseModel):
    """Gimbal speed request body."""

    pitch_speed: float = Field(default=0.0, description="Pitch speed in °/s")
    yaw_speed: float = Field(default=0.0, description="Yaw speed in °/s")


class ErrorResponse(BaseModel):
    """Standard error response body."""

    detail: str


# Module-level streamer singleton.
video_streamer = VideoStreamer(robot_controller, settings)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
    """Application lifespan events."""
    logger.info("startup", app=settings.app_name)
    yield
    logger.info("shutdown")
    video_streamer.stop()
    try:
        robot_controller.disconnect()
    except Exception as exc:  # pragma: no cover - defensive cleanup
        logger.warning("shutdown_disconnect_error", error=str(exc))


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["health"])
async def health() -> Dict[str, str]:
    """Return service health status."""
    return {"status": "ok", "service": "robot-bridge"}


@app.get("/ready", tags=["health"])
async def ready() -> Dict[str, Any]:
    """Return readiness including robot connection state."""
    return {"status": "ok", "connected": robot_controller.is_connected}


@app.post("/connect", tags=["robot"])
async def connect(request: ConnectRequest) -> Dict[str, Any]:
    """Connect to the robot."""
    try:
        return robot_controller.connect(request.conn_type)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@app.post("/disconnect", tags=["robot"])
async def disconnect() -> Dict[str, Any]:
    """Disconnect from the robot."""
    return robot_controller.disconnect()


@app.post("/chassis/move", tags=["robot"])
async def chassis_move(request: ChassisMoveRequest) -> Dict[str, str]:
    """Move the chassis with clamped speeds."""
    try:
        robot_controller.move_chassis(request.x, request.y, request.z)
    except RuntimeError as exc:
        raise _not_connected(str(exc)) from exc
    return {"status": "ok"}


@app.post("/chassis/stop", tags=["robot"])
async def chassis_stop() -> Dict[str, str]:
    """Stop the chassis."""
    try:
        robot_controller.stop_chassis()
    except RuntimeError as exc:
        raise _not_connected(str(exc)) from exc
    return {"status": "ok"}


@app.post("/gimbal/move", tags=["robot"])
async def gimbal_move(request: GimbalMoveRequest) -> Dict[str, str]:
    """Move the gimbal with clamped speeds."""
    try:
        robot_controller.move_gimbal(request.pitch_speed, request.yaw_speed)
    except RuntimeError as exc:
        raise _not_connected(str(exc)) from exc
    return {"status": "ok"}


@app.post("/gimbal/stop", tags=["robot"])
async def gimbal_stop() -> Dict[str, str]:
    """Stop the gimbal."""
    try:
        robot_controller.stop_gimbal()
    except RuntimeError as exc:
        raise _not_connected(str(exc)) from exc
    return {"status": "ok"}


@app.post("/blaster/fire", tags=["robot"])
async def blaster_fire() -> Dict[str, str]:
    """Fire the blaster once."""
    try:
        robot_controller.fire_blaster()
    except RuntimeError as exc:
        raise _not_connected(str(exc)) from exc
    return {"status": "ok"}


@app.get("/status", tags=["robot"])
async def robot_status() -> Dict[str, Any]:
    """Return robot status."""
    return robot_controller.get_status()


@app.get("/video/stream", tags=["video"])
async def video_stream() -> StreamingResponse:
    """Stream live MJPEG video from the robot camera."""
    if not video_streamer.is_running:
        try:
            video_streamer.start()
        except RuntimeError as exc:
            raise _not_connected(str(exc)) from exc
        except Exception as exc:  # pragma: no cover - camera init failure
            logger.error("video_stream_start_error", error=str(exc))
            raise HTTPException(
                status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Could not start video stream: {exc}",
            ) from exc

    return StreamingResponse(
        video_streamer.generate_mjpeg(),
        media_type="multipart/x-mixed-replace; boundary=frame_boundary",
    )


def _not_connected(detail: str) -> HTTPException:
    """Return a standard 'robot not connected' exception."""
    return HTTPException(
        status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=detail,
    )


@app.exception_handler(HTTPException)
async def _http_exception_handler(request: Any, exc: HTTPException) -> JSONResponse:  # noqa: ARG001
    """Return JSON error responses for HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
