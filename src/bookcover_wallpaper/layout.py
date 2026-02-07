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

        # Start with cover size that fits target_rows vertically
        available_height = self.height - ((target_rows + 1) * self.gap)
        cover_height = available_height // target_rows
        cover_width = int(cover_height * self.aspect_ratio[0] / self.aspect_ratio[1])

        # Calculate how many columns fit horizontally
        num_columns = max(1, (self.width + self.gap) // (cover_width + self.gap))

        # Check if we have enough capacity (columns * rows >= books)
        capacity = num_columns * target_rows

        if capacity < num_books:
            # Not enough capacity - need to either add columns or shrink covers
            # Calculate minimum columns needed
            min_columns = (num_books + target_rows - 1) // target_rows

            if min_columns > num_columns:
                # Need more columns - recalculate cover size from width constraint
                num_columns = min_columns
                cover_width = (self.width - (num_columns + 1) * self.gap) // num_columns
                cover_height = int(cover_width * self.aspect_ratio[1] / self.aspect_ratio[0])
        else:
            # We have extra capacity - can make covers larger to fill width
            # Recalculate based on width constraint
            width_based_cover_width = (self.width - (num_columns + 1) * self.gap) // num_columns
            width_based_cover_height = int(width_based_cover_width * self.aspect_ratio[1] / self.aspect_ratio[0])

            # Check if larger covers still maintain reasonable capacity
            # Allow covers to be taller as long as capacity >= num_books
            new_capacity_rows = (self.height - ((target_rows + 2) * self.gap)) // width_based_cover_height
            new_capacity = num_columns * new_capacity_rows

            if new_capacity >= num_books:
                # Larger covers still work
                cover_width = width_based_cover_width
                cover_height = width_based_cover_height

        return num_columns, cover_width, cover_height
