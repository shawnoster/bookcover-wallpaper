"""Cover image downloading and caching."""

from pathlib import Path
import hashlib
import asyncio
import httpx
from .sources.base import Book


class CoverManager:
    """Manages downloading and caching book cover images."""

    def __init__(self, cache_dir: Path | None = None):
        """Initialize cover manager.

        Args:
            cache_dir: Cache directory path (default: ~/.cache/bookcover-wallpaper/)
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "bookcover-wallpaper"
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def get_cover(self, book: Book) -> Path | None:
        """Get cover image for a book, downloading if needed.

        Args:
            book: Book object with cover_url or cover_path

        Returns:
            Path to cover image file, or None if unavailable
        """
        # If book already has a local cover_path, use it
        if book.cover_path and book.cover_path.exists():
            return book.cover_path

        # If no cover_url, can't download
        if not book.cover_url:
            return None

        # Generate cache filename from URL hash
        url_hash = hashlib.md5(book.cover_url.encode()).hexdigest()
        # Try to preserve extension from URL
        url_lower = book.cover_url.lower()
        if ".jpg" in url_lower or ".jpeg" in url_lower:
            ext = ".jpg"
        elif ".png" in url_lower:
            ext = ".png"
        else:
            ext = ".jpg"  # Default to jpg

        cache_path = self.cache_dir / f"{url_hash}{ext}"

        # Check cache first
        if cache_path.exists():
            return cache_path

        # Download cover
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(book.cover_url)
                response.raise_for_status()

                # Save to cache
                cache_path.write_bytes(response.content)
                return cache_path

        except Exception as e:
            print(f"Warning: Failed to download cover from {book.cover_url}: {e}")
            return None

    async def download_covers(self, books: list[Book]) -> list[Book]:
        """Download covers for multiple books concurrently.

        Args:
            books: List of Book objects

        Returns:
            List of books with cover_path populated (skips failed downloads)
        """
        # Download all covers concurrently
        tasks = [self.get_cover(book) for book in books]
        cover_paths = await asyncio.gather(*tasks, return_exceptions=True)

        # Update books with cover paths and filter out failures
        books_with_covers: list[Book] = []
        for book, cover_path in zip(books, cover_paths):
            # Skip if download failed or returned exception
            if isinstance(cover_path, Exception) or cover_path is None:
                continue

            # Update book with cover_path
            book.cover_path = cover_path
            books_with_covers.append(book)

        return books_with_covers
