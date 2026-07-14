"""Unit tests for the RobotController SDK wrapper."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.config import Settings
from app.robot import RobotController


def test_connect_success(robot_controller: RobotController, mock_robot_module: MagicMock) -> None:
    """Connecting succeeds and initializes the robot."""
    result = robot_controller.connect("ap")

    assert result["connected"] is True
    assert result["conn_type"] == "ap"
    mock_robot_module.initialize.assert_called_once_with(conn_type="ap")


def test_connect_skips_when_already_connected(
    robot_controller: RobotController, mock_robot_module: MagicMock
) -> None:
    """A second connect call keeps the existing connection."""
    robot_controller.connect("ap")
    result = robot_controller.connect("ap")

    assert result["connected"] is True
    assert mock_robot_module.initialize.call_count == 1


def test_connect_invalid_conn_type(robot_controller: RobotController) -> None:
    """An unsupported conn_type raises ValueError."""
    with pytest.raises(ValueError, match="Invalid conn_type"):
        robot_controller.connect("invalid")


def test_disconnect(robot_controller: RobotController, mock_robot_module: MagicMock) -> None:
    """Disconnect closes the robot and clears the reference."""
    robot_controller.connect("ap")
    result = robot_controller.disconnect()

    assert result["connected"] is False
    mock_robot_module.close.assert_called_once()
    assert not robot_controller.is_connected


def test_disconnect_when_not_connected(robot_controller: RobotController) -> None:
    """Disconnecting without a connection is a no-op."""
    result = robot_controller.disconnect()
    assert result["connected"] is False


def test_move_chassis_clamps_speed(
    robot_controller: RobotController, mock_robot_module: MagicMock, settings: Settings
) -> None:
    """Linear chassis speed is clamped to the configured safety limit."""
    robot_controller.connect("ap")
    robot_controller.move_chassis(1.0, 0.0, 0.0)

    call_args = mock_robot_module.chassis.drive_speed.call_args
    assert abs(call_args.kwargs["x"]) <= settings.max_linear_speed_mps
    assert call_args.kwargs["y"] == 0.0
    assert call_args.kwargs["z"] == 0.0


def test_move_chassis_clamps_rotation(
    robot_controller: RobotController, mock_robot_module: MagicMock, settings: Settings
) -> None:
    """Rotation speed is clamped to the configured safety limit."""
    robot_controller.connect("ap")
    robot_controller.move_chassis(0.0, 0.0, 500.0)

    call_args = mock_robot_module.chassis.drive_speed.call_args
    assert abs(call_args.kwargs["z"]) <= settings.max_angular_speed_dps


def test_stop_chassis(robot_controller: RobotController, mock_robot_module: MagicMock) -> None:
    """Stop sends zero speeds to the chassis."""
    robot_controller.connect("ap")
    robot_controller.stop_chassis()

    mock_robot_module.chassis.drive_speed.assert_called_with(x=0.0, y=0.0, z=0.0)


def test_move_gimbal_clamps_speed(
    robot_controller: RobotController, mock_robot_module: MagicMock, settings: Settings
) -> None:
    """Gimbal speed is clamped to the configured safety limit."""
    robot_controller.connect("ap")
    robot_controller.move_gimbal(200.0, -200.0)

    call_args = mock_robot_module.gimbal.drive_speed.call_args
    assert abs(call_args.kwargs["pitch_speed"]) <= settings.max_gimbal_speed_dps
    assert abs(call_args.kwargs["yaw_speed"]) <= settings.max_gimbal_speed_dps


def test_stop_gimbal(robot_controller: RobotController, mock_robot_module: MagicMock) -> None:
    """Stop sends zero speeds to the gimbal."""
    robot_controller.connect("ap")
    robot_controller.stop_gimbal()

    mock_robot_module.gimbal.drive_speed.assert_called_with(pitch_speed=0.0, yaw_speed=0.0)


def test_fire_blaster(robot_controller: RobotController, mock_robot_module: MagicMock) -> None:
    """Fire calls the blaster module."""
    robot_controller.connect("ap")
    robot_controller.fire_blaster()

    mock_robot_module.blaster.fire.assert_called_once()


def test_get_status_connected(
    robot_controller: RobotController, mock_robot_module: MagicMock
) -> None:
    """Status reflects connection and battery."""
    robot_controller.connect("ap")
    status = robot_controller.get_status()

    assert status["connected"] is True
    assert status["battery_percent"] == 87


def test_command_when_not_connected(robot_controller: RobotController) -> None:
    """Commands without connection raise RuntimeError."""
    with pytest.raises(RuntimeError, match="not connected"):
        robot_controller.move_chassis(0.1, 0.0, 0.0)
