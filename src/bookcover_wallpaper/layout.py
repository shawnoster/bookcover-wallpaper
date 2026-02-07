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

        Prioritizes filling the entire canvas, accepting that some covers
        may be clipped at the bottom for complete coverage.

        Args:
            num_books: Number of books to display

        Returns:
            Tuple of (num_columns, cover_width, cover_height)
        """
        # Determine target columns based on book count
        # More books = more columns for better distribution
        if num_books <= 12:
            target_columns = 5
        elif num_books <= 20:
            target_columns = 7
        elif num_books <= 30:
            target_columns = 9
        elif num_books <= 40:
            target_columns = 11
        elif num_books <= 50:
            target_columns = 13
        else:
            target_columns = min(16, num_books // 3)

        # Calculate cover size to fill horizontal space
        cover_width = (self.width - (target_columns + 1) * self.gap) // target_columns
        cover_height = int(cover_width * self.aspect_ratio[1] / self.aspect_ratio[0])

        # Scale up by fixed factor to ensure full coverage with bottom clipping
        # 1.45x makes covers larger so even shortest column extends beyond bottom
        coverage_scale = 1.45
        cover_height = int(cover_height * coverage_scale)
        cover_width = int(cover_height * self.aspect_ratio[0] / self.aspect_ratio[1])

        # Recalculate actual columns that fit with scaled covers
        actual_columns = max(1, (self.width + self.gap) // (cover_width + self.gap))

        # Final cover size based on actual columns
        base_cover_width = (self.width - (actual_columns + 1) * self.gap) // actual_columns
        base_cover_height = int(base_cover_width * self.aspect_ratio[1] / self.aspect_ratio[0])

        # Apply coverage scale to both dimensions to maintain aspect ratio
        cover_width = int(base_cover_width * coverage_scale)
        cover_height = int(base_cover_height * coverage_scale)

        return actual_columns, cover_width, cover_height
