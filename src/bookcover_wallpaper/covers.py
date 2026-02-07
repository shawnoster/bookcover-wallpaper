"""Cover image downloading and caching."""

from pathlib import Path
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
        # TODO: Implement cover retrieval
        # - Check cache first
        # - Download from cover_url if not cached
        # - Handle local cover_path
        # - Return path to cover file
        return None

    async def download_covers(self, books: list[Book]) -> list[Book]:
        """Download covers for multiple books concurrently.

        Args:
            books: List of Book objects

        Returns:
            List of books with cover_path populated (skips failed downloads)
        """
        # TODO: Implement concurrent downloading
        # - Use asyncio.gather for parallel downloads
        # - Skip books where download fails
        # - Update book.cover_path
        return []
