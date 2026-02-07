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
    target_ratio = aspect_ratio[0] / aspect_ratio[1]
    img_width, img_height = image.size
    img_ratio = img_width / img_height

    if abs(img_ratio - target_ratio) < 0.01:
        # Already correct ratio
        return image

    if img_ratio > target_ratio:
        # Image is too wide, crop width
        new_width = int(img_height * target_ratio)
        left = (img_width - new_width) // 2
        box = (left, 0, left + new_width, img_height)
    else:
        # Image is too tall, crop height
        new_height = int(img_width / target_ratio)
        top = (img_height - new_height) // 2
        box = (0, top, img_width, top + new_height)

    return image.crop(box)


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
    layout_info: list[tuple[Path, tuple[int, int], tuple[int, int]]],
    output_size: tuple[int, int],
    aspect_ratio: tuple[int, int] = (2, 3),
    background_color: tuple[int, int, int] = (30, 30, 30),
) -> Image.Image:
    """Create wallpaper from covers and layout information.

    Args:
        layout_info: List of (path, position, size) tuples
        output_size: Output canvas size (width, height)
        aspect_ratio: Target aspect ratio for covers (default: 2:3)
        background_color: RGB background color (default: dark gray)

    Returns:
        Composite wallpaper as PIL Image
    """
    # Create canvas with background color
    canvas = Image.new("RGB", output_size, background_color)

    # Process each cover
    for cover_path, (x, y), (width, height) in layout_info:
        try:
            # Load image
            with Image.open(cover_path) as img:
                # Convert to RGB if needed
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # Crop to aspect ratio
                img = crop_to_aspect_ratio(img, aspect_ratio)

                # Resize to target dimensions
                img = resize_image(img, (width, height))

                # Paste onto canvas
                canvas.paste(img, (x, y))

        except Exception as e:
            # Skip covers that fail to load
            print(f"Warning: Failed to process {cover_path}: {e}")
            continue

    return canvas
