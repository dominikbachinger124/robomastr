"""Application configuration for the robot bridge."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Robot bridge settings loaded from environment variables.

    A local ``.env`` file can be used for overrides. All numeric limits are
    expressed in SI units (m/s, °/s).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "RoboMastr Robot Bridge"
    host: str = "0.0.0.0"
    port: int = 8001
    default_conn_type: str = "ap"

    # Safety limits (defense in depth, backend enforces them as well)
    max_linear_speed_mps: float = 0.5
    max_angular_speed_dps: float = 180.0
    max_gimbal_speed_dps: float = 90.0

    # Video capture settings
    video_resolution: str = "720p"
    video_fps: int = 30
    video_quality: int = 85

    # Observability
    log_level: str = "INFO"


settings = Settings()
