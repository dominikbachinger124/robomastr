"""Shared pytest fixtures for robot bridge tests."""

from __future__ import annotations

from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.logging import get_logger
from app.robot import RobotController
from app.robot import robot_controller as _module_robot_controller

logger = get_logger(__name__)


@pytest.fixture
def settings() -> Settings:
    """Return a fresh settings instance for tests."""
    return Settings()


@pytest.fixture
def mock_robot_module() -> MagicMock:
    """Return a mock robot instance with all used subsystems."""
    robot = MagicMock()
    robot.chassis = MagicMock()
    robot.gimbal = MagicMock()
    robot.blaster = MagicMock()
    robot.camera = MagicMock()
    robot.battery = MagicMock()
    robot.battery.get_battery.return_value = 87
    return robot


@pytest.fixture
def mock_robot_class(mock_robot_module: MagicMock) -> Generator[MagicMock, None, None]:
    """Patch the robomaster Robot class so it returns the mock module."""
    with patch("app.robot.rm_robot") as patched_module:
        patched_module.Robot.return_value = mock_robot_module
        yield patched_module


@pytest.fixture
def robot_controller(settings: Settings, mock_robot_class: MagicMock) -> RobotController:
    """Return a fresh RobotController using the mocked SDK."""
    return RobotController(settings)


@pytest.fixture
def client(mock_robot_class: MagicMock) -> Generator[TestClient, None, None]:
    """Return a FastAPI TestClient with a mocked robot."""
    from app.main import app

    # Ensure the module-level singleton starts each test disconnected and
    # without a stale robot reference.
    _module_robot_controller.disconnect()
    _module_robot_controller._robot = None  # noqa: SLF001 - test reset

    yield TestClient(app)

    # Clean up after the test so later tests don't inherit connected state.
    from app.main import video_streamer

    video_streamer.stop()
    _module_robot_controller.disconnect()
    _module_robot_controller._robot = None  # noqa: SLF001 - test reset
