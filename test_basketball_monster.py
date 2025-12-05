#!/usr/bin/env python3
"""Test script for Basketball Monster scraper."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nba_predictor.scraper.basketballmonster_scraper import BasketballMonsterScraper
from nba_predictor.core.logger import setup_logging

def main():
    """Test the Basketball Monster scraper."""
    setup_logging()

    print("Testing Basketball Monster scraper...")
    scraper = BasketballMonsterScraper()

    try:
        count = scraper.import_daily_lineups()
        print(f"\n✅ Successfully imported {count} lineup entries!")

        # Check the debug files
        import os
        if os.path.exists("/tmp/basketballmonster_debug.html"):
            size = os.path.getsize("/tmp/basketballmonster_debug.html")
            print(f"\n📄 Debug HTML saved: {size} bytes")
            print("   View at: /tmp/basketballmonster_debug.html")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
