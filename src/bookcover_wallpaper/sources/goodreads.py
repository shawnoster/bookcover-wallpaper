"""Goodreads CSV export and RSS feed source."""

from pathlib import Path
import csv
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
from .base import Book


class GoodreadsSource:
    """Source that reads from Goodreads CSV export or RSS feed."""

    def __init__(self, source: str | Path, shelf: str = "read"):
        """Initialize with CSV path, user ID, or RSS URL.

        Args:
            source: Path to CSV file, Goodreads user ID, or RSS feed URL
            shelf: Shelf to read from (default: "read"). Only used for RSS feeds.
        """
        self.source = source
        self.shelf = shelf
        self.is_rss = self._detect_rss()

    def _detect_rss(self) -> bool:
        """Detect if source is RSS (user ID or URL) or CSV (file path)."""
        source_str = str(self.source)

        # Check if it's a URL
        if source_str.startswith("http://") or source_str.startswith("https://"):
            return True

        # Check if it's a file path
        if isinstance(self.source, Path) or "/" in source_str or "\\" in source_str or source_str.endswith(".csv"):
            return False

        # Assume it's a user ID (numeric or short string)
        return True

    async def get_books(self, limit: int = 18) -> list[Book]:
        """Get books from Goodreads CSV or RSS feed.

        Args:
            limit: Maximum number of books to retrieve

        Returns:
            List of Book objects parsed from source
        """
        if self.is_rss:
            return await self._get_books_from_rss(limit)
        else:
            return await self._get_books_from_csv(limit)

    async def _get_books_from_csv(self, limit: int) -> list[Book]:
        """Get books from CSV export."""
        csv_path = Path(self.source)
        if not csv_path.exists():
            return []

        books: list[Book] = []
        read_books: list[tuple[datetime | None, Book]] = []

        with open(csv_path, encoding="utf-8") as f:
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

    async def _get_books_from_rss(self, limit: int) -> list[Book]:
        """Get books from Goodreads RSS feed."""
        # Build RSS URL
        source_str = str(self.source)
        if source_str.startswith("http"):
            rss_url = source_str
        else:
            # Assume it's a user ID
            rss_url = f"https://www.goodreads.com/review/list_rss/{source_str}?shelf={self.shelf}"

        books: list[Book] = []

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(rss_url)
                response.raise_for_status()

                # Parse XML/RSS
                soup = BeautifulSoup(response.content, "xml")

                # Find all book items
                items = soup.find_all("item")

                for item in items:
                    if len(books) >= limit:
                        break

                    # Extract metadata from RSS item
                    title_elem = item.find("title")
                    title = title_elem.text if title_elem else ""

                    author_elem = item.find("author_name")
                    author = author_elem.text if author_elem else None

                    # Get ISBN
                    isbn_elem = item.find("isbn")
                    isbn = isbn_elem.text if isbn_elem else None

                    # Get book ID for cover URL
                    book_id_elem = item.find("book_id")
                    book_id = book_id_elem.text if book_id_elem else None

                    # Try to get cover from multiple possible fields
                    cover_url = None
                    book_large_image = item.find("book_large_image_url")
                    if book_large_image and book_large_image.text:
                        cover_url = book_large_image.text

                    if not cover_url:
                        book_image = item.find("book_image_url")
                        if book_image and book_image.text:
                            cover_url = book_image.text

                    if not cover_url and book_id:
                        # Construct cover URL from book ID
                        cover_url = f"https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/{book_id}.jpg"

                    # Create Book object
                    book = Book(
                        title=title,
                        author=author,
                        isbn=isbn,
                        cover_url=cover_url,
                    )
                    books.append(book)

        except Exception as e:
            print(f"Warning: Failed to fetch Goodreads RSS feed: {e}")

        return books
