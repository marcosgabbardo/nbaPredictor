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

    # Mapping of team abbreviations to full names
    TEAM_ABBR_MAP = {
        "ATL": "Atlanta Hawks",
        "BOS": "Boston Celtics",
        "BKN": "Brooklyn Nets",
        "CHA": "Charlotte Hornets",
        "CHI": "Chicago Bulls",
        "CLE": "Cleveland Cavaliers",
        "DAL": "Dallas Mavericks",
        "DEN": "Denver Nuggets",
        "DET": "Detroit Pistons",
        "GSW": "Golden State Warriors",
        "HOU": "Houston Rockets",
        "IND": "Indiana Pacers",
        "LAC": "Los Angeles Clippers",
        "LAL": "Los Angeles Lakers",
        "MEM": "Memphis Grizzlies",
        "MIA": "Miami Heat",
        "MIL": "Milwaukee Bucks",
        "MIN": "Minnesota Timberwolves",
        "NOP": "New Orleans Pelicans",
        "NYK": "New York Knicks",
        "OKC": "Oklahoma City Thunder",
        "ORL": "Orlando Magic",
        "PHI": "Philadelphia 76ers",
        "PHX": "Phoenix Suns",
        "POR": "Portland Trail Blazers",
        "SAC": "Sacramento Kings",
        "SAS": "San Antonio Spurs",
        "TOR": "Toronto Raptors",
        "UTA": "Utah Jazz",
        "WAS": "Washington Wizards",
    }

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

    def _get_page(self, url: str, save_debug: bool = False) -> BeautifulSoup:
        """Fetch and parse a page with error handling.

        Args:
            url: URL to fetch
            save_debug: If True, save raw response to debug file

        Returns:
            Parsed BeautifulSoup object

        Raises:
            RotoWireScraperError: If request fails
        """
        try:
            logger.debug("Fetching page", url=url)

            # Add delay to avoid rate limiting
            time.sleep(2)

            # More complete headers to simulate real browser
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
            }

            # Try with cloudscraper (handles Cloudflare)
            response = self.session.get(
                url,
                headers=headers,
                timeout=30,
                allow_redirects=True
            )

            response.raise_for_status()

            # Ensure proper encoding - cloudscraper should handle this, but let's be explicit
            # If response.encoding is None or incorrect, set it to utf-8
            if response.encoding is None or response.encoding.lower() not in ['utf-8', 'utf8']:
                response.encoding = 'utf-8'

            logger.debug(
                "Response received",
                status_code=response.status_code,
                content_length=len(response.content),
                encoding=response.encoding,
                apparent_encoding=response.apparent_encoding
            )

            # Get text with proper encoding
            html_text = response.text

            # Verify we got actual HTML content, not binary garbage
            if not html_text or len(html_text) < 100:
                raise RotoWireScraperError(f"Response appears to be invalid or too short: {len(html_text)} chars")

            # Save raw response for debugging if requested
            if save_debug:
                try:
                    with open("/tmp/rotowire_raw_response.html", "w", encoding="utf-8", errors="replace") as f:
                        f.write(html_text)
                    logger.info(
                        "DEBUG: Saved raw response",
                        path="/tmp/rotowire_raw_response.html",
                        size=len(html_text),
                        first_200=html_text[:200].encode('unicode_escape').decode('ascii')
                    )
                except Exception as e:
                    logger.warning("Could not save raw response", error=str(e))

            return BeautifulSoup(html_text, "html.parser")

        except Exception as e:
            logger.error("Request failed", url=url, error=str(e), error_type=type(e).__name__)
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

        # Fetch lineups page (with debug enabled to save raw response)
        lineups_page = self._get_page(self.lineups_url, save_debug=True)

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

        # DEBUG: Save HTML to file for inspection
        try:
            debug_path = "/tmp/rotowire_debug.html"

            # Save the prettified HTML
            with open(debug_path, "w", encoding="utf-8", errors="replace") as f:
                # Use prettify() which returns a proper unicode string
                html_content = lineups_page.prettify()
                f.write(html_content)

            logger.info(
                "DEBUG: Saved HTML to /tmp/rotowire_debug.html",
                size_chars=len(html_content),
                first_100_chars=html_content[:100]
            )
        except Exception as e:
            logger.warning("Could not save debug HTML", error=str(e), exc_info=True)

        # DEBUG: Try multiple selector patterns
        logger.info("DEBUG: Testing different selector patterns...")

        # Pattern 1: Exact class match with dict
        pattern1 = lineups_page.find_all("div", {"class": "lineup is-nba"})
        logger.info("DEBUG Pattern 1: dict {'class': 'lineup is-nba'}", count=len(pattern1))

        # Pattern 2: List of classes
        pattern2 = lineups_page.find_all("div", class_=["lineup", "is-nba"])
        logger.info("DEBUG Pattern 2: list ['lineup', 'is-nba']", count=len(pattern2))

        # Pattern 3: CSS selector
        pattern3 = lineups_page.select("div.lineup.is-nba")
        logger.info("DEBUG Pattern 3: CSS selector 'div.lineup.is-nba'", count=len(pattern3))

        # Pattern 4: Just "lineup" class
        pattern4 = lineups_page.find_all("div", class_="lineup")
        logger.info("DEBUG Pattern 4: class='lineup'", count=len(pattern4))

        # Pattern 5: Contains "lineup" and "nba"
        pattern5 = lineups_page.find_all("div", class_=lambda x: x and isinstance(x, list) and "lineup" in x and "is-nba" in x)
        logger.info("DEBUG Pattern 5: lambda with list check", count=len(pattern5))

        # Show all divs that have "lineup" in any class
        all_lineup_divs = lineups_page.find_all("div", class_=lambda x: x and "lineup" in str(x).lower())
        logger.info("DEBUG: All divs with 'lineup' in class", count=len(all_lineup_divs))

        # Show first few class combinations
        seen_classes = set()
        for div in all_lineup_divs[:20]:
            classes = div.get('class', [])
            if classes:
                class_str = " ".join(sorted(classes))
                if class_str not in seen_classes:
                    seen_classes.add(class_str)
                    logger.info("DEBUG: Found div with classes", classes=class_str)

        # Find all lineup boxes (game cards)
        # Try CSS selector first as it's most reliable
        lineup_boxes = lineups_page.select("div.lineup.is-nba")
        if not lineup_boxes:
            # Fallback to find_all with lambda
            lineup_boxes = lineups_page.find_all("div", class_=lambda x: x and isinstance(x, list) and "lineup" in x and "is-nba" in x)

        logger.info("Found lineup boxes", count=len(lineup_boxes))

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

        # Find team abbreviations first
        team_abbrs = box.find_all("div", class_="lineup__abbr")
        if len(team_abbrs) != 2:
            logger.warning("Expected 2 teams, found different number", count=len(team_abbrs))
            return lineups

        away_abbr = team_abbrs[0].text.strip()
        home_abbr = team_abbrs[1].text.strip()

        # Convert abbreviations to full team names
        away_team = self.TEAM_ABBR_MAP.get(away_abbr, away_abbr)
        home_team = self.TEAM_ABBR_MAP.get(home_abbr, home_abbr)

        logger.debug("Parsing lineup", away=away_team, home=home_team)

        # Find the lineup__main div which contains both team lists
        lineup_main = box.find("div", class_="lineup__main")
        if not lineup_main:
            logger.warning("No lineup__main found")
            return lineups

        # Find both team lists
        team_lists = lineup_main.find_all("ul", class_="lineup__list")

        if len(team_lists) < 2:
            logger.warning("Expected 2 team lists, found different number", count=len(team_lists))
            return lineups

        # Parse away team (is-visit)
        away_list = lineup_main.find("ul", {"class": "lineup__list is-visit"})
        if away_list:
            away_lineups = self._parse_team_list(away_list, away_team, scrape_date, game_date)
            lineups.extend(away_lineups)

        # Parse home team (is-home)
        home_list = lineup_main.find("ul", {"class": "lineup__list is-home"})
        if home_list:
            home_lineups = self._parse_team_list(home_list, home_team, scrape_date, game_date)
            lineups.extend(home_lineups)

        return lineups

    def _parse_team_list(
        self, team_list: Any, team_name: str, scrape_date: date, game_date: date
    ) -> List[Dict[str, Any]]:
        """Parse a team's lineup list (starters and injuries).

        Args:
            team_list: BeautifulSoup element for team's ul.lineup__list
            team_name: Team abbreviation
            scrape_date: Date when data was scraped
            game_date: Date of the game

        Returns:
            List of lineup entries (starters and injuries)
        """
        lineups = []
        is_parsing_starters = True
        starter_count = 0

        # Iterate through all list items
        for item in team_list.find_all("li"):
            # Check if this is the separator between starters and injuries
            if "lineup__title" in item.get("class", []):
                is_parsing_starters = False
                continue

            # Skip status messages
            if "lineup__status" in item.get("class", []):
                continue

            # Only process player items
            if "lineup__player" not in item.get("class", []):
                continue

            try:
                # Get player link and name
                player_link = item.find("a")
                if not player_link:
                    continue

                player_name = player_link.text.strip()

                # Get position
                position_elem = item.find("div", class_="lineup__pos")
                position = position_elem.text.strip() if position_elem else None

                # Get injury status from span
                injury_span = item.find("span", class_="lineup__inj")
                injury_status = injury_span.text.strip() if injury_span else None

                # Determine status
                if is_parsing_starters and starter_count < 5:
                    # This is a starter
                    status = "Starter"
                    starter_count += 1

                    # Even starters can have injury concerns
                    if injury_status:
                        status = injury_status  # Use "Ques", "Out", etc. if present
                else:
                    # This is from the injury/questionable list
                    if injury_status:
                        status = injury_status
                    else:
                        # Check probability class to determine status
                        classes = " ".join(item.get("class", []))
                        if "is-pct-play-0" in classes:
                            status = "OUT"
                        elif "is-pct-play-50" in classes:
                            status = "Questionable"
                        else:
                            status = "GTD"  # Game-Time Decision

                lineups.append(
                    {
                        "scrape_date": scrape_date,
                        "game_date": game_date,
                        "team_name": team_name,
                        "player_name": player_name,
                        "position": position,
                        "status": status,
                        "injury_description": injury_status if injury_status and status == "Starter" else None,
                        "notes": None,
                    }
                )

            except Exception as e:
                logger.debug("Failed to parse player", error=str(e), player=player_name if 'player_name' in locals() else 'unknown')
                continue

        return lineups
