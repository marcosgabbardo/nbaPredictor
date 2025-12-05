#!/usr/bin/env python3
"""Test script for the image-based lineup scraper.

This script tests the image scraper with a sample lineup screenshot.
"""

import sys
from datetime import date
from pathlib import Path

from nba_predictor.core.logger import get_logger
from nba_predictor.scraper.image_lineup_scraper import ImageLineupScraper

logger = get_logger(__name__)


def test_image_scraper(image_path: str):
    """Test the image scraper with a sample image.

    Args:
        image_path: Path to the test image
    """
    logger.info("="*60)
    logger.info("TESTING IMAGE-BASED LINEUP SCRAPER")
    logger.info("="*60)

    # Check if image exists
    image_file = Path(image_path)
    if not image_file.exists():
        logger.error(f"Image file not found: {image_path}")
        logger.info("\nPlease provide a screenshot of NBA lineups to test with.")
        logger.info("Example: python test_image_scraper.py lineup_screenshot.png")
        return False

    logger.info(f"Test image: {image_path}")
    logger.info(f"Game date: {date.today()} (today)")

    try:
        # Initialize scraper
        logger.info("\n[1/3] Initializing scraper...")
        scraper = ImageLineupScraper()
        logger.info("✓ Scraper initialized successfully")

        # Extract lineups from image (without saving to database yet)
        logger.info("\n[2/3] Extracting lineups from image using Claude Vision API...")
        logger.info("(This may take 10-20 seconds...)")

        raw_lineups = scraper._extract_lineups_from_image(image_path)

        logger.info(f"✓ Successfully extracted {len(raw_lineups)} lineup entries")

        # Display extracted data
        logger.info("\n[3/3] Extracted lineup data:")
        logger.info("-"*60)

        current_team = None
        for i, lineup in enumerate(raw_lineups):
            team = lineup.get("team_name", "Unknown")

            # Print team header when it changes
            if team != current_team:
                logger.info(f"\n{team}:")
                logger.info("-"*40)
                current_team = team

            player = lineup.get("player_name", "Unknown")
            position = lineup.get("position", "N/A")
            status = lineup.get("status", "Active")
            injury = lineup.get("injury_description")

            status_display = status
            if injury and injury != status:
                status_display = f"{status} ({injury})"

            logger.info(f"  {position:3s} | {player:20s} | {status_display}")

        logger.info("\n" + "="*60)
        logger.info("TEST COMPLETED SUCCESSFULLY!")
        logger.info("="*60)
        logger.info(f"Total players found: {len(raw_lineups)}")
        logger.info("\nTo import this data to the database, run:")
        logger.info(f"  python import_lineup_from_image.py {image_path}")
        logger.info("="*60)

        return True

    except Exception as e:
        logger.error(f"\n✗ Test failed: {e}", exc_info=True)
        logger.info("\nTroubleshooting:")
        logger.info("1. Make sure ANTHROPIC_API_KEY is set in your .env file")
        logger.info("2. Verify the image is a clear screenshot of NBA lineups")
        logger.info("3. Check that your API key has credits available")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nUsage: python test_image_scraper.py <image_path>")
        print("\nExample: python test_image_scraper.py lineup_screenshot.png")
        sys.exit(1)

    image_path = sys.argv[1]
    success = test_image_scraper(image_path)
    sys.exit(0 if success else 1)
