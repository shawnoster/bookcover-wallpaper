"""Goodreads CSV export source."""

from pathlib import Path
import csv
from datetime import datetime
from .base import Book


class GoodreadsSource:
    """Source that reads from Goodreads CSV export."""

    def __init__(self, csv_path: Path):
        """Initialize with CSV file path.

        Args:
            csv_path: Path to Goodreads CSV export file
        """
        self.csv_path = csv_path

    async def get_books(self, limit: int = 18) -> list[Book]:
        """Get books from Goodreads CSV.

        Args:
            limit: Maximum number of books to retrieve

        Returns:
            List of Book objects parsed from CSV
        """
        if not self.csv_path.exists():
            return []

        books: list[Book] = []
        read_books: list[tuple[datetime | None, Book]] = []

        with open(self.csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Extract basic metadata
                title = row.get("Title", "").strip()
                author = row.get("Author", "").strip()
                isbn = row.get("ISBN13", "") or row.get("ISBN", "")
                # Clean ISBN format (Goodreads uses ="..." format)
                isbn = isbn.strip().strip('"').strip("=").strip('"')  # Clean ISBN format

                # Get cover URL if available
                cover_url = row.get("Book Cover", "") or row.get("Cover", "")
                if not cover_url:
                    # Construct Goodreads cover URL from Book ID if available
                    book_id = row.get("Book Id", "")
                    if book_id:
                        cover_url = f"https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/{book_id}.jpg"

                # Filter to "read" books (not "to-read" or "currently-reading")
                shelf = row.get("Exclusive Shelf", "").lower()
                if shelf != "read":
                    continue

                # Parse date read for sorting
                date_read_str = row.get("Date Read", "")
                date_read = None
                if date_read_str:
                    try:
                        date_read = datetime.strptime(date_read_str, "%Y/%m/%d")
                    except ValueError:
                        # Try alternative format
                        try:
                            date_read = datetime.strptime(date_read_str, "%Y-%m-%d")
                        except ValueError:
                            pass

                # Create Book object
                book = Book(
                    title=title,
                    author=author or None,
                    isbn=isbn or None,
                    cover_url=cover_url or None,
                )

                read_books.append((date_read, book))

        # Sort by date read (most recent first)
        read_books.sort(key=lambda x: x[0] if x[0] else datetime.min, reverse=True)

        # Extract books and apply limit
        books = [book for _, book in read_books[:limit]]

        return books
