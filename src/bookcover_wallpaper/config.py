"""Configuration management."""

from pathlib import Path
from pydantic import BaseModel


class Config(BaseModel):
    """Application configuration."""

    # Cache settings
    cache_dir: Path = Path.home() / ".cache" / "bookcover-wallpaper"

    # Layout settings
    default_width: int = 1920
    default_height: int = 1080
    default_limit: int = 18
    gap_size: int = 4
    aspect_ratio: tuple[int, int] = (2, 3)

    # Background settings
    background_color: tuple[int, int, int] = (30, 30, 30)


# Global config instance
config = Config()
