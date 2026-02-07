"""Base interfaces for book data sources."""

from typing import Protocol
from pathlib import Path
from pydantic import BaseModel


class Book(BaseModel):
    """Represents a book with metadata."""

    title: str
    author: str | None = None
    isbn: str | None = None
    cover_url: str | None = None
    cover_path: Path | None = None


class BookSource(Protocol):
    """Protocol for book data sources."""

    async def get_books(self, limit: int = 18) -> list[Book]:
        """Retrieve books from the source.

        Args:
            limit: Maximum number of books to retrieve

        Returns:
            List of Book objects
        """
        ...
