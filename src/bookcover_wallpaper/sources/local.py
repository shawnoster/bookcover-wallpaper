"""Local directory source for book covers."""

from pathlib import Path
from .base import Book


class LocalSource:
    """Source that reads book covers from a local directory."""

    def __init__(self, directory: Path):
        """Initialize with a directory path.

        Args:
            directory: Path to directory containing book cover images
        """
        self.directory = directory

    async def get_books(self, limit: int = 18) -> list[Book]:
        """Get books from local directory.

        Args:
            limit: Maximum number of books to retrieve

        Returns:
            List of Book objects with local cover paths
        """
        # TODO: Implement local directory scanning
        # - Find image files (jpg, png)
        # - Create Book objects with cover_path set
        # - Extract metadata from filenames if possible
        return []
