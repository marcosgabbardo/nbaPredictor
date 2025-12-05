"""RotoWire lineup scraper for daily NBA lineups and injury reports."""

import re
import time
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import cloudscraper
from bs4 import BeautifulSoup
from sqlalchemy import and_

from nba_predictor.core.config import get_settings
from nba_predictor.core.logger import get_logger
from nba_predictor.models import DailyLineup, get_db

logger = get_logger(__name__)


class RotoWireScraperError(Exception):
    """Base exception for RotoWire scraper errors."""

    pass


class RotoWireScraper:
    """Scraper for RotoWire NBA lineups and injury reports."""

    def __init__(self) -> None:
        """Initialize the scraper with configuration."""
        self.settings = get_settings()
        self.base_url = "https://www.rotowire.com"
        self.lineups_url = f"{self.base_url}/basketball/nba-lineups.php"
        self.session = self._create_session()
        logger.info("RotoWire scraper initialized")

    def _create_session(self) -> cloudscraper.CloudScraper:
        """Create a cloudscraper session.

        Returns:
            Configured cloudscraper session
        """
        session = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "darwin", "desktop": True}
        )
        return session

    def _get_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a page with error handling.

        Args:
            url: URL to fetch

        Returns:
            Parsed BeautifulSoup object

        Raises:
            RotoWireScraperError: If request fails
        """
        try:
            logger.debug("Fetching page", url=url)

            # Add delay to avoid rate limiting
            time.sleep(1.5)

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            }

            response = self.session.get(url, headers=headers, timeout=30, allow_redirects=True)
            response.raise_for_status()

            return BeautifulSoup(response.text, "html.parser")

        except Exception as e:
            logger.error("Request failed", url=url, error=str(e))
            raise RotoWireScraperError(f"Failed to fetch {url}: {e}")

    def import_daily_lineups(self, target_date: Optional[date] = None) -> int:
        """Import daily lineups and injury status.

        Args:
            target_date: Date to import lineups for (defaults to today)

        Returns:
            Number of lineup entries imported

        Raises:
            RotoWireScraperError: If scraping fails
        """
        if target_date is None:
            target_date = date.today()

        scrape_date = date.today()

        logger.info("Starting lineup import", target_date=target_date, scrape_date=scrape_date)

        # Fetch lineups page
        lineups_page = self._get_page(self.lineups_url)

        # Delete existing lineups for this scrape date and game date combination
        with get_db() as db:
            deleted = (
                db.query(DailyLineup)
                .filter(
                    and_(
                        DailyLineup.scrape_date == scrape_date,
                        DailyLineup.game_date == target_date,
                    )
                )
                .delete(synchronize_session=False)
            )
            logger.info("Deleted existing lineups", count=deleted)

        lineups_imported = 0

        # Find all lineup boxes (game cards)
        lineup_boxes = lineups_page.find_all("div", class_="lineup")

        for box in lineup_boxes:
            try:
                game_lineups = self._parse_lineup_box(box, scrape_date, target_date)

                for lineup_data in game_lineups:
                    with get_db() as db:
                        lineup = DailyLineup(**lineup_data)
                        db.add(lineup)
                        lineups_imported += 1

                logger.debug("Parsed lineup box", entries=len(game_lineups))

            except Exception as e:
                logger.error("Failed to parse lineup box", error=str(e), exc_info=True)
                continue

        logger.info("Lineup import completed", lineups_imported=lineups_imported)
        return lineups_imported

    def _parse_lineup_box(
        self, box: Any, scrape_date: date, game_date: date
    ) -> List[Dict[str, Any]]:
        """Parse a lineup box for a single game.

        Args:
            box: BeautifulSoup element for lineup box
            scrape_date: Date when data was scraped
            game_date: Date of the game

        Returns:
            List of lineup entry dictionaries
        """
        lineups = []

        # Find team sections (away and home)
        team_sections = box.find_all("div", class_="lineup__main")

        for team_section in team_sections:
            try:
                # Get team name
                team_name_elem = team_section.find("div", class_="lineup__abbr")
                if not team_name_elem:
                    continue

                team_name = team_name_elem.text.strip()

                # Parse starters
                starters = self._parse_starters(team_section, team_name, scrape_date, game_date)
                lineups.extend(starters)

                # Parse injury list
                injuries = self._parse_injuries(team_section, team_name, scrape_date, game_date)
                lineups.extend(injuries)

            except Exception as e:
                logger.debug("Failed to parse team section", error=str(e))
                continue

        return lineups

    def _parse_starters(
        self, team_section: Any, team_name: str, scrape_date: date, game_date: date
    ) -> List[Dict[str, Any]]:
        """Parse starting lineup from team section.

        Args:
            team_section: BeautifulSoup element for team section
            team_name: Team name
            scrape_date: Date when data was scraped
            game_date: Date of the game

        Returns:
            List of starter entries
        """
        starters = []

        # Find the starters list
        starters_div = team_section.find("ul", class_="lineup__list")
        if not starters_div:
            return starters

        starter_items = starters_div.find_all("li", class_="lineup__player")

        for item in starter_items[:5]:  # Only first 5 are starters
            try:
                player_link = item.find("a")
                if not player_link:
                    continue

                player_name = player_link.text.strip()

                # Get position
                position_elem = item.find("div", class_="lineup__pos")
                position = position_elem.text.strip() if position_elem else None

                starters.append(
                    {
                        "scrape_date": scrape_date,
                        "game_date": game_date,
                        "team_name": team_name,
                        "player_name": player_name,
                        "position": position,
                        "status": "Starter",
                        "injury_description": None,
                        "notes": None,
                    }
                )

            except Exception as e:
                logger.debug("Failed to parse starter", error=str(e))
                continue

        return starters

    def _parse_injuries(
        self, team_section: Any, team_name: str, scrape_date: date, game_date: date
    ) -> List[Dict[str, Any]]:
        """Parse injury list from team section.

        Args:
            team_section: BeautifulSoup element for team section
            team_name: Team name
            scrape_date: Date when data was scraped
            game_date: Date of the game

        Returns:
            List of injury entries
        """
        injuries = []

        # Find the injury list
        injury_div = team_section.find("ul", class_="lineup__injuries")
        if not injury_div:
            return injuries

        injury_items = injury_div.find_all("li")

        for item in injury_items:
            try:
                # Get player name
                player_link = item.find("a")
                if not player_link:
                    continue

                player_name = player_link.text.strip()

                # Get injury status (OUT, GTD, Questionable, etc.)
                status_elem = item.find("span", class_="lineup__inj-status")
                status = status_elem.text.strip() if status_elem else "Unknown"

                # Get injury description
                injury_desc_elem = item.find("span", class_="lineup__inj")
                injury_description = injury_desc_elem.text.strip() if injury_desc_elem else None

                # Get position
                position_elem = item.find("div", class_="lineup__pos")
                position = position_elem.text.strip() if position_elem else None

                injuries.append(
                    {
                        "scrape_date": scrape_date,
                        "game_date": game_date,
                        "team_name": team_name,
                        "player_name": player_name,
                        "position": position,
                        "status": status,
                        "injury_description": injury_description,
                        "notes": None,
                    }
                )

            except Exception as e:
                logger.debug("Failed to parse injury", error=str(e))
                continue

        return injuries
