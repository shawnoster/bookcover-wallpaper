"""Image processing utilities."""

from pathlib import Path
from PIL import Image


def crop_to_aspect_ratio(image: Image.Image, aspect_ratio: tuple[int, int]) -> Image.Image:
    """Crop image to target aspect ratio.

    Args:
        image: PIL Image to crop
        aspect_ratio: Target ratio as (width, height) tuple

    Returns:
        Cropped PIL Image
    """
    # TODO: Implement aspect ratio cropping
    # - Calculate target dimensions
    # - Center crop to match ratio
    return image


def resize_image(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Resize image to target size.

    Args:
        image: PIL Image to resize
        size: Target size as (width, height) tuple

    Returns:
        Resized PIL Image
    """
    return image.resize(size, Image.Resampling.LANCZOS)


def create_wallpaper(
    cover_paths: list[Path],
    layout_info: list[tuple[Path, tuple[int, int], tuple[int, int]]],
    output_size: tuple[int, int],
    background_color: tuple[int, int, int] = (30, 30, 30),
) -> Image.Image:
    """Create wallpaper from covers and layout information.

    Args:
        cover_paths: List of cover image paths
        layout_info: List of (path, position, size) tuples
        output_size: Output canvas size (width, height)
        background_color: RGB background color (default: dark gray)

    Returns:
        Composite wallpaper as PIL Image
    """
    # TODO: Implement wallpaper composition
    # 1. Create canvas with background color
    # 2. For each cover in layout_info:
    #    - Load image
    #    - Crop to 2:3 aspect ratio
    #    - Resize to target size
    #    - Paste at position
    # 3. Return composite image
    canvas = Image.new("RGB", output_size, background_color)
    return canvas
