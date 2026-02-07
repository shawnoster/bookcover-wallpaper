"""Tests for end-to-end wallpaper generation."""

import asyncio
from pathlib import Path
from PIL import Image
import pytest

from bookcover_wallpaper.sources.local import LocalSource
from bookcover_wallpaper.layout import MasonryLayout
from bookcover_wallpaper.image import create_wallpaper, crop_to_aspect_ratio


def test_crop_to_aspect_ratio():
    """Test aspect ratio cropping."""
    # Create a test image (wider than 2:3)
    img = Image.new("RGB", (600, 400), "red")

    # Crop to 2:3
    cropped = crop_to_aspect_ratio(img, (2, 3))

    # Should crop width
    assert cropped.width < img.width
    assert cropped.height == img.height

    # Check ratio (allow small tolerance)
    ratio = cropped.width / cropped.height
    expected_ratio = 2 / 3
    assert abs(ratio - expected_ratio) < 0.01


@pytest.mark.asyncio
async def test_local_source(tmp_path):
    """Test local directory source."""
    # Create test images
    for i in range(5):
        img = Image.new("RGB", (200, 300), f"#{i*50:02x}{i*40:02x}{i*30:02x}")
        img.save(tmp_path / f"book_{i}.png")

    # Test source
    source = LocalSource(tmp_path)
    books = await source.get_books(limit=10)

    assert len(books) == 5
    assert all(book.cover_path is not None for book in books)
    assert all(book.cover_path.exists() for book in books)


def test_masonry_layout():
    """Test masonry layout calculation."""
    layout = MasonryLayout(width=1920, height=1080, gap=4)

    # Create dummy cover paths
    cover_paths = [Path(f"/tmp/cover_{i}.jpg") for i in range(12)]

    # Calculate layout
    layout_info = layout.calculate_layout(cover_paths)

    # Should have entry for each cover
    assert len(layout_info) == 12

    # Check structure
    for path, (x, y), (w, h) in layout_info:
        assert isinstance(path, Path)
        assert x >= 0 and x < 1920
        assert y >= 0
        assert w > 0 and h > 0
        # Check aspect ratio
        ratio = w / h
        expected_ratio = 2 / 3
        assert abs(ratio - expected_ratio) < 0.01


def test_create_wallpaper(tmp_path):
    """Test wallpaper creation."""
    # Create test images
    test_covers = []
    colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255),
              (255, 255, 100), (255, 100, 255), (100, 255, 255)]
    for i, color in enumerate(colors):
        img_path = tmp_path / f"cover_{i}.png"
        img = Image.new("RGB", (200, 300), color)
        img.save(img_path)
        test_covers.append(img_path)

    # Create layout
    layout = MasonryLayout(width=800, height=600, gap=4)
    layout_info = layout.calculate_layout(test_covers)

    # Create wallpaper
    wallpaper = create_wallpaper(
        layout_info=layout_info,
        output_size=(800, 600),
        aspect_ratio=(2, 3),
    )

    assert wallpaper.size == (800, 600)
    assert wallpaper.mode == "RGB"

    # Save to verify
    output_path = tmp_path / "wallpaper.png"
    wallpaper.save(output_path)
    assert output_path.exists()
