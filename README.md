# Book Cover Wallpaper Generator

Generate beautiful landscape wallpapers from tiled book covers using Goodreads, web search, or local images.

## Features

- **Multiple sources**: Goodreads reading history, web search, or local directory
- **Masonry layout**: Pinterest-style organic layouts with variable heights
- **Smart caching**: Downloaded covers are cached to avoid re-fetching
- **Genre filtering**: Filter search results by genre
- **Customizable**: Configure resolution, book count, and more

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd bookcover-wallpaper

# Install with uv
uv sync

# Or install from PyPI (when published)
uv pip install bookcover-wallpaper
```

## Usage

### Local Directory

Generate wallpaper from a directory of book cover images:

```bash
bookcover-wallpaper --source local --path ~/book-covers/ --output wallpaper.png
```

### Goodreads Recently Read

1. Export your Goodreads library (Settings → Import/Export → Export Library)
2. Generate wallpaper:

```bash
bookcover-wallpaper --source goodreads --goodreads-csv ~/goodreads.csv --limit 20
```

### Web Search

Search for popular or recommended books:

```bash
# Fantasy books
bookcover-wallpaper --source search --query "best fantasy books" --genre fantasy --limit 15

# Science fiction
bookcover-wallpaper --source search --query "popular science fiction" --genre "science fiction"
```

## Options

- `--source`: Source of book covers (local, goodreads, search)
- `--path`: Path to directory with covers (local source)
- `--goodreads-csv`: Path to Goodreads CSV export (goodreads source)
- `--query`: Search query for books (search source)
- `--genre`: Genre filter, comma-separated (search source)
- `--limit`: Number of books to include (default: 18)
- `--width`: Output width in pixels (default: 1920)
- `--height`: Output height in pixels (default: 1080)
- `--output`: Output file path (default: wallpaper.png)

## Development

### Using Make (Recommended)

```bash
# Show all available commands
make help

# Install dependencies
make install

# Install with dev dependencies
make dev

# Run tests
make test

# Run tests with coverage
make test-cov

# Type checking
make lint

# Run both linting and tests
make check

# Clean cache and build artifacts
make clean
```

### Direct Commands

```bash
# Run tests
uv run pytest

# Type checking
uv run mypy src/

# Install in development mode
uv sync --dev
```

## Status

🚧 **In Development** - Core functionality being implemented

See the project tracker for current status and roadmap.

## License

MIT
