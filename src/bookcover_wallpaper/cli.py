"""Command-line interface for bookcover-wallpaper."""

import asyncio
import click
from pathlib import Path

from .sources.local import LocalSource
from .sources.goodreads import GoodreadsSource
from .sources.search import SearchSource
from .covers import CoverManager
from .layout import MasonryLayout
from .image import create_wallpaper
from .config import config


@click.command()
@click.option(
    "--source",
    type=click.Choice(["local", "goodreads", "search"]),
    default="local",
    help="Source of book covers",
)
@click.option(
    "--path",
    type=click.Path(exists=True, path_type=Path),
    help="Path to directory with book covers (for local source)",
)
@click.option(
    "--goodreads-csv",
    type=click.Path(exists=True, path_type=Path),
    help="Path to Goodreads CSV export (for goodreads source)",
)
@click.option(
    "--query",
    type=str,
    help="Search query for books (for search source)",
)
@click.option(
    "--genre",
    type=str,
    help="Genre filter (comma-separated)",
)
@click.option(
    "--limit",
    type=int,
    default=18,
    help="Number of books to include (default: 18)",
)
@click.option(
    "--width",
    type=int,
    default=1920,
    help="Output width in pixels (default: 1920)",
)
@click.option(
    "--height",
    type=int,
    default=1080,
    help="Output height in pixels (default: 1080)",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default="wallpaper.png",
    help="Output file path (default: wallpaper.png)",
)
def main(
    source: str,
    path: Path | None,
    goodreads_csv: Path | None,
    query: str | None,
    genre: str | None,
    limit: int,
    width: int,
    height: int,
    output: Path,
) -> None:
    """Generate landscape wallpapers from tiled book covers.

    Examples:

      # Local directory
      bookcover-wallpaper --source local --path ~/book-covers/

      # Goodreads recent reads
      bookcover-wallpaper --source goodreads --goodreads-csv ~/goodreads.csv

      # Search for fantasy books
      bookcover-wallpaper --source search --query "best fantasy" --genre fantasy
    """
    asyncio.run(_generate_wallpaper(
        source, path, goodreads_csv, query, genre, limit, width, height, output
    ))


async def _generate_wallpaper(
    source: str,
    path: Path | None,
    goodreads_csv: Path | None,
    query: str | None,
    genre: str | None,
    limit: int,
    width: int,
    height: int,
    output: Path,
) -> None:
    """Internal async function to generate wallpaper."""
    click.echo(f"Generating wallpaper from {source} source...")
    click.echo(f"Output: {output} ({width}x{height})")
    click.echo(f"Books to include: up to {limit}")

    # Get books from source
    books = []
    if source == "local":
        if not path:
            click.echo("Error: --path required for local source", err=True)
            return
        click.echo(f"Scanning directory: {path}")
        local_source = LocalSource(path)
        books = await local_source.get_books(limit)
    elif source == "goodreads":
        if not goodreads_csv:
            click.echo("Error: --goodreads-csv required for goodreads source", err=True)
            return
        click.echo(f"Parsing Goodreads CSV: {goodreads_csv}")
        goodreads_source = GoodreadsSource(goodreads_csv)
        books = await goodreads_source.get_books(limit)

        # Download covers for Goodreads books
        if books:
            click.echo(f"Downloading {len(books)} book covers...")
            cover_manager = CoverManager(config.cache_dir)
            books = await cover_manager.download_covers(books)
    elif source == "search":
        if not query:
            click.echo("Error: --query required for search source", err=True)
            return
        click.echo(f"Searching for: {query}" + (f" (genre: {genre})" if genre else ""))
        search_source = SearchSource(query, genre)
        books = await search_source.get_books(limit)

        # Download covers for search results
        if books:
            click.echo(f"Downloading {len(books)} book covers...")
            cover_manager = CoverManager(config.cache_dir)
            books = await cover_manager.download_covers(books)

    if not books:
        click.echo("Error: No books found", err=True)
        return

    click.echo(f"Found {len(books)} book covers")

    # Extract cover paths
    cover_paths = [book.cover_path for book in books if book.cover_path]

    if not cover_paths:
        click.echo("Error: No valid cover images found", err=True)
        return

    # Calculate layout
    click.echo("Calculating masonry layout...")
    layout = MasonryLayout(
        width=width,
        height=height,
        gap=config.gap_size,
        aspect_ratio=config.aspect_ratio,
    )
    layout_info = layout.calculate_layout(cover_paths)

    # Create wallpaper
    click.echo("Composing wallpaper...")
    wallpaper = create_wallpaper(
        layout_info=layout_info,
        output_size=(width, height),
        aspect_ratio=config.aspect_ratio,
        background_color=config.background_color,
    )

    # Save to file
    click.echo(f"Saving to {output}...")
    wallpaper.save(output)

    click.echo(f"✓ Wallpaper generated successfully: {output}")


if __name__ == "__main__":
    main()
