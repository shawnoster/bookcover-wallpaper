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

        Args:
            num_books: Number of books to display

        Returns:
            Tuple of (num_columns, cover_width, cover_height)
        """
        # Determine target rows based on book count
        if num_books <= 12:
            target_rows = 3
        elif num_books <= 20:
            target_rows = 4
        elif num_books <= 30:
            target_rows = 5
        elif num_books <= 40:
            target_rows = 6
        elif num_books <= 50:
            target_rows = 7
        elif num_books <= 60:
            target_rows = 8
        elif num_books <= 70:
            target_rows = 9
        else:
            target_rows = 10

        # Calculate ideal cover height to fit target rows
        # height = (rows * cover_height) + ((rows + 1) * gap)
        available_height = self.height - ((target_rows + 1) * self.gap)
        target_cover_height = available_height // target_rows

        # Calculate cover width from height using aspect ratio
        target_cover_width = int(target_cover_height * self.aspect_ratio[0] / self.aspect_ratio[1])

        # Calculate how many columns we can fit horizontally
        # width = (cols * cover_width) + ((cols + 1) * gap)
        max_columns = max(1, (self.width + self.gap) // (target_cover_width + self.gap))

        # Limit columns to ensure each column has enough books to fill vertically
        # We want at least target_rows books per column on average for good coverage
        # Use a factor of 0.8 to allow some variation in masonry placement
        ideal_books_per_column = target_rows * 0.8
        max_columns_for_books = max(1, int(num_books / ideal_books_per_column))

        num_columns = min(max_columns, max_columns_for_books)

        # Calculate actual maximum books that will be in any column (ceiling division)
        max_books_per_column = (num_books + num_columns - 1) // num_columns

        # Recalculate cover size to ensure max_books_per_column books fit vertically
        available_height = self.height - ((max_books_per_column + 1) * self.gap)
        cover_height = available_height // max_books_per_column

        # Recalculate width from height to maintain aspect ratio
        cover_width = int(cover_height * self.aspect_ratio[0] / self.aspect_ratio[1])

        # Verify we don't exceed canvas width with this many columns
        total_width = (num_columns * cover_width) + ((num_columns + 1) * self.gap)
        if total_width > self.width:
            # Covers are too wide, recalculate from width constraint
            cover_width = (self.width - (num_columns + 1) * self.gap) // num_columns
            cover_height = int(cover_width * self.aspect_ratio[1] / self.aspect_ratio[0])

        return num_columns, cover_width, cover_height
