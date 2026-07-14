"""Unit tests for the video streamer."""

from __future__ import annotations

from unittest.mock import MagicMock

import numpy as np

from app.config import Settings
from app.video import VideoStreamer, encode_frame_to_jpeg


def test_encode_frame_to_jpeg() -> None:
    """Encoding produces valid JPEG bytes."""
    frame = np.zeros((10, 10, 3), dtype=np.uint8)
    jpeg = encode_frame_to_jpeg(frame)

    assert jpeg.startswith(b"\xff\xd8")
    assert jpeg.endswith(b"\xff\xd9")


def test_get_frame_returns_none_before_start(
    robot_controller: MagicMock, settings: Settings
) -> None:
    """No frames are available before the streamer starts."""
    streamer = VideoStreamer(robot_controller, settings)
    assert streamer.get_frame() is None
    assert not streamer.is_running


def test_generate_mjpeg_yields_boundary_and_jpeg(
    robot_controller: MagicMock, settings: Settings, mock_robot_module: MagicMock
) -> None:
    """The MJPEG generator yields multipart blocks containing JPEG data."""
    robot_controller.connect = MagicMock(return_value={"connected": True})
    robot_controller.get_camera = MagicMock(return_value=mock_robot_module.camera)

    # Lower the frame interval so the background thread primes a frame quickly
    settings.video_fps = 1000

    fake_frame = np.zeros((20, 20, 3), dtype=np.uint8)
    mock_robot_module.camera.read_cv2_image.return_value = fake_frame

    streamer = VideoStreamer(robot_controller, settings)
    streamer.start()

    # Pull two iterations from the generator
    generator = streamer.generate_mjpeg()
    block1 = next(generator)
    block2 = next(generator)

    streamer.stop()

    assert b"--frame_boundary" in block1
    assert b"Content-Type: image/jpeg" in block1
    assert b"\xff\xd8" in block1
    assert b"\xff\xd9" in block1
    assert block1.startswith(b"--frame_boundary")
    assert block2.startswith(b"--frame_boundary")
