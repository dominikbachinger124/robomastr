"""Video capture and MJPEG streaming for the robot bridge."""

from __future__ import annotations

import queue
import threading
import time
from typing import Any, Generator

import cv2
import numpy as np

from app.config import Settings
from app.logging import get_logger
from app.robot import RobotController

logger = get_logger(__name__)


def encode_frame_to_jpeg(frame: np.ndarray[Any, Any], quality: int = 85) -> bytes:
    """Encode a BGR/RGB numpy frame to JPEG bytes.

    Args:
        frame: Image array from the SDK.
        quality: JPEG quality (0-100).

    Returns:
        JPEG encoded image bytes.
    """
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    success, encoded = cv2.imencode(".jpg", frame, encode_params)
    if not success:
        raise RuntimeError("Failed to encode frame to JPEG")
    return encoded.tobytes()


class VideoStreamer:
    """Captures frames from the robot camera and serves them as MJPEG.

    Use this when you need a live video feed for the web dashboard.
    The streamer runs a background thread so the FastAPI endpoint can
    stream frames without blocking request handlers.

    Do NOT use this for saving high-quality recordings; recording logic
    belongs in the main backend.
    """

    def __init__(self, robot_controller: RobotController, settings: Settings) -> None:
        """Initialize the streamer (does not start capture)."""
        self._robot_controller = robot_controller
        self._settings = settings
        self._running = False
        self._thread: threading.Thread | None = None
        self._latest_frame: bytes | None = None
        self._frame_lock = threading.Lock()
        self._camera: Any = None

    @property
    def is_running(self) -> bool:
        """Return True if the capture thread is active."""
        return self._running

    def start(self) -> None:
        """Start the camera capture thread.

        The robot must already be connected before calling this method.
        """
        if self._running:
            logger.info("video_start_skipped", reason="already_running")
            return

        self._camera = self._robot_controller.get_camera()
        logger.info(
            "video_start",
            resolution=self._settings.video_resolution,
            fps=self._settings.video_fps,
        )
        self._camera.start_video_stream(display=False, resolution=self._settings.video_resolution)
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the camera capture thread and release the camera."""
        if not self._running:
            logger.info("video_stop_skipped", reason="not_running")
            return

        logger.info("video_stop")
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        if self._camera is not None:
            try:
                self._camera.stop_video_stream()
            except Exception as exc:  # pragma: no cover - defensive cleanup
                logger.warning("video_stop_error", error=str(exc))
        with self._frame_lock:
            self._latest_frame = None
        self._camera = None

    def _capture_loop(self) -> None:
        """Background loop that fetches and encodes frames."""
        interval = 1.0 / max(1, self._settings.video_fps)
        while self._running:
            try:
                frame = self._camera.read_cv2_image(strategy="newest")
                if frame is not None:
                    jpeg = encode_frame_to_jpeg(frame, self._settings.video_quality)
                    with self._frame_lock:
                        self._latest_frame = jpeg
            except queue.Empty:
                # No frame available yet; keep looping.
                pass
            except Exception as exc:  # pragma: no cover - camera may glitch
                logger.warning("video_capture_error", error=str(exc))
            time.sleep(interval)

    def get_frame(self) -> bytes | None:
        """Return the most recent JPEG frame, if any."""
        with self._frame_lock:
            return self._latest_frame

    def generate_mjpeg(self) -> Generator[bytes, None, None]:
        """Yield MJPEG multipart frames forever while running.

        Yields:
            Bytes objects suitable for a StreamingResponse.
        """
        boundary = b"--frame_boundary\r\n"
        header = b"Content-Type: image/jpeg\r\n\r\n"
        while self._running:
            frame = self.get_frame()
            if frame is None:
                time.sleep(1.0 / max(1, self._settings.video_fps))
                continue
            yield boundary + header + frame + b"\r\n"
