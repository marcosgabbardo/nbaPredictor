#!/usr/bin/env python3
"""Script to import NBA lineups from image screenshots.

Usage:
    python import_lineup_from_image.py <image_path> [game_date]

Examples:
    # Import from a single image for today's games
    python import_lineup_from_image.py lineup_screenshot.png

    # Import from a single image for a specific date
    python import_lineup_from_image.py lineup_screenshot.png 2025-12-05

    # Import from multiple images
    python import_lineup_from_image.py game1.png game2.png game3.png
"""

import sys
from datetime import date, datetime
from pathlib import Path

from nba_predictor.core.logger import get_logger
from nba_predictor.scraper.image_lineup_scraper import (
    ImageLineupScraper,
    ImageLineupScraperError,
)

logger = get_logger(__name__)


def parse_date(date_str: str) -> date:
    """Parse a date string in YYYY-MM-DD format.

    Args:
        date_str: Date string

    Returns:
        Parsed date object
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    # Parse arguments
    image_paths = []
    game_date = None

    for arg in sys.argv[1:]:
        # Check if it's a date
        if arg.count("-") == 2 and len(arg) == 10:
            try:
                game_date = parse_date(arg)
                logger.info(f"Using game date: {game_date}")
                continue
            except ValueError:
                pass

        # Otherwise, treat as image path
        image_path = Path(arg)
        if not image_path.exists():
            logger.error(f"Image file not found: {image_path}")
            sys.exit(1)

        image_paths.append(image_path)

    if not image_paths:
        logger.error("No image paths provided")
        print(__doc__)
        sys.exit(1)

    # Use today's date if not specified
    if game_date is None:
        game_date = date.today()
        logger.info(f"No date specified, using today: {game_date}")

    # Initialize scraper
    try:
        scraper = ImageLineupScraper()
    except Exception as e:
        logger.error(f"Failed to initialize scraper: {e}")
        logger.error("Make sure ANTHROPIC_API_KEY is set in your environment or .env file")
        sys.exit(1)

    # Process images
    total_imported = 0
    for image_path in image_paths:
        try:
            logger.info(f"Processing image: {image_path}")
            count = scraper.import_lineups_from_image(image_path, game_date)
            total_imported += count
            logger.info(f"Successfully imported {count} lineup entries from {image_path}")
        except ImageLineupScraperError as e:
            logger.error(f"Failed to process {image_path}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error processing {image_path}: {e}", exc_info=True)
            continue

    logger.info(f"\n{'='*60}")
    logger.info(f"IMPORT COMPLETE")
    logger.info(f"{'='*60}")
    logger.info(f"Total images processed: {len(image_paths)}")
    logger.info(f"Total lineup entries imported: {total_imported}")
    logger.info(f"Game date: {game_date}")
    logger.info(f"{'='*60}\n")


if __name__ == "__main__":
    main()
