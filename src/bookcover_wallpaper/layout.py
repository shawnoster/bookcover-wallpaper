"""Layout algorithms for arranging book covers."""

from pathlib import Path
from PIL import Image


class MasonryLayout:
    """Pinterest-style masonry layout for book covers."""

    def __init__(
        self,
        width: int,
        height: int,
        gap: int = 4,
        aspect_ratio: tuple[int, int] = (2, 3),
    ):
        """Initialize masonry layout.

        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels
            gap: Gap between covers in pixels (default: 4)
            aspect_ratio: Standard book cover ratio (default: 2:3)
        """
        self.width = width
        self.height = height
        self.gap = gap
        self.aspect_ratio = aspect_ratio

    def calculate_layout(self, cover_paths: list[Path]) -> list[tuple[Path, tuple[int, int], tuple[int, int]]]:
        """Calculate positions and sizes for all covers.

        Args:
            cover_paths: List of paths to cover images

        Returns:
            List of (path, (x, y), (w, h)) tuples
        """
        if not cover_paths:
            return []

        # Calculate columns and cover dimensions
        num_columns = self._calculate_columns()
        cover_width = (self.width - (num_columns + 1) * self.gap) // num_columns
        cover_height = int(cover_width * self.aspect_ratio[1] / self.aspect_ratio[0])

        # Initialize column heights
        column_heights = [self.gap] * num_columns

        layout = []
        for cover_path in cover_paths:
            # Find shortest column
            shortest_col = min(range(num_columns), key=lambda i: column_heights[i])

            # Calculate position
            x = self.gap + shortest_col * (cover_width + self.gap)
            y = column_heights[shortest_col]

            # Add to layout
            layout.append((cover_path, (x, y), (cover_width, cover_height)))

            # Update column height
            column_heights[shortest_col] += cover_height + self.gap

        return layout

    def _calculate_columns(self) -> int:
        """Calculate optimal number of columns for the canvas width."""
        # Target cover width: 200-250px for good visibility
        target_cover_width = 225

        # Calculate columns based on canvas width
        # Account for gaps: width = (n * cover_width) + ((n + 1) * gap)
        num_columns = max(1, (self.width + self.gap) // (target_cover_width + self.gap))

        return num_columns
