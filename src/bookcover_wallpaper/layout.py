"""Layout algorithms for arranging book covers."""

import math
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

        num_books = len(cover_paths)

        # Calculate optimal layout based on book count
        num_columns, cover_width, cover_height = self._calculate_optimal_layout(num_books)

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

    def _calculate_optimal_layout(self, num_books: int) -> tuple[int, int, int]:
        """Calculate optimal columns and cover size based on book count.

        Uses area-based calculation to ensure covers fill the entire canvas.
        Accepts that some covers may be clipped at the bottom for full coverage.

        Args:
            num_books: Number of books to display

        Returns:
            Tuple of (num_columns, cover_width, cover_height)
        """
        ar_w, ar_h = self.aspect_ratio
        canvas_area = self.width * self.height

        # Total cover area should overfill the canvas for full coverage
        # Higher overfill = larger covers, more clipping, denser look
        overfill = 1.4
        target_total_area = canvas_area * overfill

        # Each cover has area = w * h = w * (w * ar_h/ar_w) = w² * ar_h/ar_w
        # n covers: n * w² * ar_h/ar_w = target_total_area
        # w = sqrt(target_total_area * ar_w / (n * ar_h))
        cover_width = int(math.sqrt(target_total_area * ar_w / (num_books * ar_h)))
        cover_height = int(cover_width * ar_h / ar_w)

        # Calculate columns that fit
        num_columns = max(1, (self.width + self.gap) // (cover_width + self.gap))

        # Snap cover width to fill horizontal space evenly
        cover_width = (self.width - (num_columns + 1) * self.gap) // num_columns
        cover_height = int(cover_width * ar_h / ar_w)

        return num_columns, cover_width, cover_height
