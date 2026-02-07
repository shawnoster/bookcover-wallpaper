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
        image_extensions = {".jpg", ".jpeg", ".png", ".webp"}
        books: list[Book] = []

        # Scan directory for image files
        if not self.directory.exists():
            return []

        for image_path in sorted(self.directory.iterdir()):
            if len(books) >= limit:
                break

            if not image_path.is_file():
                continue

            if image_path.suffix.lower() not in image_extensions:
                continue

            # Extract title from filename (remove extension)
            title = image_path.stem

            # Create Book object
            book = Book(
                title=title,
                author=None,
                cover_path=image_path,
            )
            books.append(book)

        return books
