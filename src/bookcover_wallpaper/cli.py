"""Command-line interface for bookcover-wallpaper."""

import click
from pathlib import Path


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
    click.echo(f"Generating wallpaper from {source} source...")
    click.echo(f"Output: {output} ({width}x{height})")
    click.echo(f"Books to include: {limit}")

    # TODO: Implement actual generation
    click.echo("\nNOTE: Implementation in progress")


if __name__ == "__main__":
    main()
