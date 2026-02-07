"""Web search source for book discovery."""

import httpx
from .base import Book


class SearchSource:
    """Source that searches for books via web APIs."""

    def __init__(self, query: str, genre: str | None = None):
        """Initialize with search parameters.

        Args:
            query: Search query string
            genre: Optional genre filter
        """
        self.query = query
        self.genre = genre

    async def get_books(self, limit: int = 18) -> list[Book]:
        """Search for books using web APIs.

        Args:
            limit: Maximum number of books to retrieve

        Returns:
            List of Book objects from search results
        """
        # Search both APIs concurrently
        # Request more than limit to account for deduplication
        search_limit = limit + 10

        google_books = await self._search_google_books(search_limit)
        open_library_books = await self._search_open_library(search_limit)

        # Combine results
        all_books = google_books + open_library_books

        # Deduplicate based on ISBN or title+author
        seen_isbns: set[str] = set()
        seen_titles: set[tuple[str, str]] = set()
        unique_books: list[Book] = []

        for book in all_books:
            # Skip if we have enough books
            if len(unique_books) >= limit:
                break

            # Deduplicate by ISBN
            if book.isbn:
                if book.isbn in seen_isbns:
                    continue
                seen_isbns.add(book.isbn)

            # Deduplicate by title + author
            title_key = (
                book.title.lower().strip(),
                (book.author or "").lower().strip(),
            )
            if title_key in seen_titles:
                continue
            seen_titles.add(title_key)

            unique_books.append(book)

        return unique_books[:limit]

    async def _search_google_books(self, limit: int) -> list[Book]:
        """Search Google Books API."""
        books: list[Book] = []
        base_url = "https://www.googleapis.com/books/v1/volumes"

        # Build query
        query_parts = [self.query]
        if self.genre:
            query_parts.append(f"subject:{self.genre}")
        search_query = " ".join(query_parts)

        params = {
            "q": search_query,
            "maxResults": min(40, limit * 2),  # Get extra for filtering
            "orderBy": "relevance",
            "printType": "books",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(base_url, params=params)
                response.raise_for_status()
                data = response.json()

                items = data.get("items", [])
                for item in items:
                    if len(books) >= limit:
                        break

                    volume_info = item.get("volumeInfo", {})

                    # Extract metadata
                    title = volume_info.get("title", "")
                    authors = volume_info.get("authors", [])
                    author = authors[0] if authors else None

                    # Get ISBN
                    isbn = None
                    for identifier in volume_info.get("industryIdentifiers", []):
                        if identifier.get("type") in ["ISBN_13", "ISBN_10"]:
                            isbn = identifier.get("identifier")
                            break

                    # Get cover URL (prefer large, fallback to thumbnail)
                    image_links = volume_info.get("imageLinks", {})
                    cover_url = (
                        image_links.get("large")
                        or image_links.get("medium")
                        or image_links.get("thumbnail")
                    )

                    # Upgrade to HTTPS if needed
                    if cover_url and cover_url.startswith("http://"):
                        cover_url = cover_url.replace("http://", "https://")

                    # Skip books without covers
                    if not cover_url:
                        continue

                    book = Book(
                        title=title,
                        author=author,
                        isbn=isbn,
                        cover_url=cover_url,
                    )
                    books.append(book)

        except Exception as e:
            print(f"Warning: Google Books API error: {e}")

        return books

    async def _search_open_library(self, limit: int) -> list[Book]:
        """Search Open Library API."""
        books: list[Book] = []
        base_url = "https://openlibrary.org/search.json"

        # Build query
        query_parts = [self.query]
        if self.genre:
            query_parts.append(self.genre)
        search_query = " ".join(query_parts)

        params = {
            "q": search_query,
            "limit": min(100, limit * 2),  # Get extra for filtering
            "fields": "title,author_name,isbn,cover_i,subject",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(base_url, params=params)
                response.raise_for_status()
                data = response.json()

                docs = data.get("docs", [])
                for doc in docs:
                    if len(books) >= limit:
                        break

                    # Extract metadata
                    title = doc.get("title", "")
                    authors = doc.get("author_name", [])
                    author = authors[0] if authors else None

                    # Get ISBN
                    isbns = doc.get("isbn", [])
                    isbn = isbns[0] if isbns else None

                    # Get cover URL
                    cover_id = doc.get("cover_i")
                    if not cover_id:
                        continue

                    cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"

                    # Optional: Filter by genre if specified
                    if self.genre:
                        subjects = doc.get("subject", [])
                        if subjects and isinstance(subjects, list):
                            # Check if genre matches any subject (case-insensitive)
                            genre_lower = self.genre.lower()
                            if not any(genre_lower in str(s).lower() for s in subjects):
                                continue

                    book = Book(
                        title=title,
                        author=author,
                        isbn=isbn,
                        cover_url=cover_url,
                    )
                    books.append(book)

        except Exception as e:
            print(f"Warning: Open Library API error: {e}")

        return books
