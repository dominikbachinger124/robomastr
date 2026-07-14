"""API tests for the robot bridge FastAPI app."""

from __future__ import annotations

from typing import Any, Generator
from unittest.mock import MagicMock

from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    """Health endpoint returns ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "robot-bridge"}


def test_ready_not_connected(client: TestClient) -> None:
    """Ready endpoint reflects disconnected state."""
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "connected": False}


def test_connect(client: TestClient, mock_robot_module: MagicMock) -> None:
    """Connect initializes the robot."""
    response = client.post("/connect", json={"conn_type": "ap"})
    assert response.status_code == 200
    data = response.json()
    assert data["connected"] is True
    mock_robot_module.initialize.assert_called_once_with(conn_type="ap")


def test_connect_invalid_conn_type(client: TestClient) -> None:
    """Invalid connection type returns 400."""
    response = client.post("/connect", json={"conn_type": "invalid"})
    assert response.status_code == 422


def test_chassis_move(client: TestClient, mock_robot_module: MagicMock) -> None:
    """Chassis move forwards to the SDK."""
    client.post("/connect", json={"conn_type": "ap"})
    response = client.post("/chassis/move", json={"x": 0.3, "y": 0.0, "z": 0.0})

    assert response.status_code == 200
    mock_robot_module.chassis.drive_speed.assert_called_once()


def test_chassis_move_not_connected(client: TestClient) -> None:
    """Chassis move without robot returns 503."""
    response = client.post("/chassis/move", json={"x": 0.1, "y": 0.0, "z": 0.0})
    assert response.status_code == 503


def test_gimbal_move(client: TestClient, mock_robot_module: MagicMock) -> None:
    """Gimbal move forwards to the SDK."""
    client.post("/connect", json={"conn_type": "ap"})
    response = client.post("/gimbal/move", json={"pitch_speed": 10.0, "yaw_speed": 20.0})

    assert response.status_code == 200
    mock_robot_module.gimbal.drive_speed.assert_called_once()


def test_blaster_fire(client: TestClient, mock_robot_module: MagicMock) -> None:
    """Blaster fire forwards to the SDK."""
    client.post("/connect", json={"conn_type": "ap"})
    response = client.post("/blaster/fire")

    assert response.status_code == 200
    mock_robot_module.blaster.fire.assert_called_once()


def test_status(client: TestClient, mock_robot_module: MagicMock) -> None:
    """Status endpoint returns robot state."""
    client.post("/connect", json={"conn_type": "ap"})
    response = client.get("/status")

    assert response.status_code == 200
    data = response.json()
    assert data["connected"] is True
    assert data["battery_percent"] == 87


def test_video_stream(client: TestClient, mock_robot_module: MagicMock, monkeypatch: Any) -> None:
    """Video stream endpoint starts the streamer and returns MJPEG."""
    client.post("/connect", json={"conn_type": "ap"})

    import numpy as np

    mock_robot_module.camera.read_cv2_image.return_value = np.zeros((10, 10, 3), dtype=np.uint8)

    # The real generator loops forever, so provide a finite mock stream for
    # the HTTP smoke test to avoid blocking the test client.
    from app.main import video_streamer

    def _finite_mjpeg() -> Generator[bytes, None, None]:
        boundary = b"--frame_boundary\r\n"
        header = b"Content-Type: image/jpeg\r\n\r\n"
        frame = b"\xff\xd8\xff\xd9"  # minimal valid JPEG
        yield boundary + header + frame + b"\r\n"

    monkeypatch.setattr(video_streamer, "generate_mjpeg", _finite_mjpeg)

    response = client.get("/video/stream")
    assert response.status_code == 200
    assert "multipart/x-mixed-replace" in response.headers["content-type"]
