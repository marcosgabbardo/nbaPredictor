"""Basketball Monster lineup scraper for daily NBA lineups and injury reports."""

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


class BasketballMonsterScraperError(Exception):
    """Base exception for Basketball Monster scraper errors."""

    pass


class BasketballMonsterScraper:
    """Scraper for Basketball Monster NBA lineups and injury reports."""

    # Mapping of team abbreviations to full names
    TEAM_ABBR_MAP = {
        "ATL": "Atlanta Hawks",
        "BOS": "Boston Celtics",
        "BKN": "Brooklyn Nets",
        "BRK": "Brooklyn Nets",  # Alternative abbreviation
        "CHA": "Charlotte Hornets",
        "CHO": "Charlotte Hornets",  # Alternative abbreviation
        "CHI": "Chicago Bulls",
        "CLE": "Cleveland Cavaliers",
        "DAL": "Dallas Mavericks",
        "DEN": "Denver Nuggets",
        "DET": "Detroit Pistons",
        "GSW": "Golden State Warriors",
        "GS": "Golden State Warriors",  # Alternative abbreviation
        "HOU": "Houston Rockets",
        "IND": "Indiana Pacers",
        "LAC": "Los Angeles Clippers",
        "LAL": "Los Angeles Lakers",
        "LA": "Los Angeles Lakers",  # Alternative abbreviation
        "MEM": "Memphis Grizzlies",
        "MIA": "Miami Heat",
        "MIL": "Milwaukee Bucks",
        "MIN": "Minnesota Timberwolves",
        "NOP": "New Orleans Pelicans",
        "NO": "New Orleans Pelicans",  # Alternative abbreviation
        "NYK": "New York Knicks",
        "NY": "New York Knicks",  # Alternative abbreviation
        "OKC": "Oklahoma City Thunder",
        "ORL": "Orlando Magic",
        "PHI": "Philadelphia 76ers",
        "PHX": "Phoenix Suns",
        "POR": "Portland Trail Blazers",
        "SAC": "Sacramento Kings",
        "SAS": "San Antonio Spurs",
        "SA": "San Antonio Spurs",  # Alternative abbreviation
        "TOR": "Toronto Raptors",
        "UTA": "Utah Jazz",
        "WAS": "Washington Wizards",
    }

    def __init__(self) -> None:
        """Initialize the scraper with configuration."""
        self.settings = get_settings()
        self.base_url = "https://basketballmonster.com"
        self.lineups_url = f"{self.base_url}/nbalineups.aspx"
        self.session = self._create_session()
        logger.info("Basketball Monster scraper initialized")

    def _create_session(self) -> cloudscraper.CloudScraper:
        """Create a cloudscraper session.

        Returns:
            Configured cloudscraper session
        """
        import os

        # Remove proxy settings to avoid 403 errors
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)
        os.environ.pop('http_proxy', None)
        os.environ.pop('https_proxy', None)

        session = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "desktop": True}
        )
        # Ensure session doesn't use proxies
        session.trust_env = False
        return session

    def _get_page(self, url: str, save_debug: bool = False) -> BeautifulSoup:
        """Fetch and parse a page with error handling.

        Args:
            url: URL to fetch
            save_debug: If True, save raw response to debug file

        Returns:
            Parsed BeautifulSoup object

        Raises:
            BasketballMonsterScraperError: If request fails
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

            # Try with cloudscraper (handles Cloudflare and other protections)
            response = self.session.get(
                url, headers=headers, timeout=30, allow_redirects=True
            )

            response.raise_for_status()

            # Ensure proper encoding
            if response.encoding is None or response.encoding.lower() not in [
                "utf-8",
                "utf8",
            ]:
                response.encoding = "utf-8"

            logger.debug(
                "Response received",
                status_code=response.status_code,
                content_length=len(response.content),
                encoding=response.encoding,
            )

            # Get text with proper encoding
            html_text = response.text

            # Verify we got actual HTML content
            if not html_text or len(html_text) < 100:
                raise BasketballMonsterScraperError(
                    f"Response appears to be invalid or too short: {len(html_text)} chars"
                )

            # Save raw response for debugging if requested
            if save_debug:
                try:
                    with open(
                        "/tmp/basketballmonster_raw_response.html",
                        "w",
                        encoding="utf-8",
                        errors="replace",
                    ) as f:
                        f.write(html_text)
                    logger.info(
                        "DEBUG: Saved raw response",
                        path="/tmp/basketballmonster_raw_response.html",
                        size=len(html_text),
                        first_200=html_text[:200]
                        .encode("unicode_escape")
                        .decode("ascii"),
                    )
                except Exception as e:
                    logger.warning("Could not save raw response", error=str(e))

            return BeautifulSoup(html_text, "html.parser")

        except Exception as e:
            logger.error(
                "Request failed", url=url, error=str(e), error_type=type(e).__name__
            )
            raise BasketballMonsterScraperError(f"Failed to fetch {url}: {e}")

    def import_daily_lineups(self, target_date: Optional[date] = None) -> int:
        """Import daily lineups and injury status.

        Args:
            target_date: Date to import lineups for (defaults to today)

        Returns:
            Number of lineup entries imported

        Raises:
            BasketballMonsterScraperError: If scraping fails
        """
        if target_date is None:
            target_date = date.today()

        scrape_date = date.today()

        logger.info(
            "Starting lineup import", target_date=target_date, scrape_date=scrape_date
        )

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
            debug_path = "/tmp/basketballmonster_debug.html"
            with open(debug_path, "w", encoding="utf-8", errors="replace") as f:
                html_content = lineups_page.prettify()
                f.write(html_content)

            logger.info(
                "DEBUG: Saved HTML to /tmp/basketballmonster_debug.html",
                size_chars=len(html_content),
                first_100_chars=html_content[:100],
            )
        except Exception as e:
            logger.warning("Could not save debug HTML", error=str(e), exc_info=True)

        # Basketball Monster specific parsing
        # Basketball Monster uses a table-based layout with game matchups
        logger.info("DEBUG: Testing different selector patterns for Basketball Monster...")

        # Strategy 1: Look for the main lineups table/container
        # Basketball Monster typically has a table with class containing "lineups" or "matchups"
        main_tables = lineups_page.find_all("table")
        logger.info(f"DEBUG: Found {len(main_tables)} tables")

        # Strategy 2: Look for divs with game containers
        game_containers = lineups_page.find_all("div", class_=lambda x: x and any(
            keyword in str(x).lower() for keyword in ["game", "matchup", "contest"]
        ))
        logger.info(f"DEBUG: Found {len(game_containers)} game containers")

        # Strategy 3: Look for repeating patterns - each game usually has two team sections
        team_sections = lineups_page.find_all(["div", "tr"], class_=lambda x: x and any(
            keyword in str(x).lower() for keyword in ["team", "roster"]
        ))
        logger.info(f"DEBUG: Found {len(team_sections)} team sections")

        # Parse games from tables (most common Basketball Monster structure)
        parsed_games = []

        for table in main_tables:
            try:
                # Look for rows that might contain matchup info
                rows = table.find_all("tr")

                if len(rows) < 5:  # Skip small tables
                    continue

                # Try to parse this table as a game
                game_lineups = self._parse_basketball_monster_table(
                    table, scrape_date, target_date
                )

                if game_lineups:
                    parsed_games.append(game_lineups)
                    for lineup_data in game_lineups:
                        with get_db() as db:
                            lineup = DailyLineup(**lineup_data)
                            db.add(lineup)
                            lineups_imported += 1

                    logger.info(f"Parsed game with {len(game_lineups)} players")

            except Exception as e:
                logger.debug(f"Failed to parse table as game: {e}")
                continue

        # If no games found in tables, try alternative parsing
        if not parsed_games:
            logger.warning("No games found in tables, trying alternative parsing strategies")

            # Try parsing from div containers
            for container in game_containers:
                try:
                    game_lineups = self._parse_game_container(
                        container, scrape_date, target_date
                    )

                    if game_lineups:
                        for lineup_data in game_lineups:
                            with get_db() as db:
                                lineup = DailyLineup(**lineup_data)
                                db.add(lineup)
                                lineups_imported += 1

                        logger.info(f"Parsed game container with {len(game_lineups)} players")

                except Exception as e:
                    logger.debug(f"Failed to parse game container: {e}")
                    continue

        logger.info("Lineup import completed", lineups_imported=lineups_imported)
        return lineups_imported

    def _parse_basketball_monster_table(
        self, table: Any, scrape_date: date, game_date: date
    ) -> List[Dict[str, Any]]:
        """Parse a Basketball Monster table for lineup data.

        Args:
            table: BeautifulSoup table element
            scrape_date: Date when data was scraped
            game_date: Date of the game

        Returns:
            List of lineup entry dictionaries
        """
        lineups = []
        rows = table.find_all("tr")

        # Try to identify teams from the table
        text_content = table.get_text()
        found_teams = []

        for abbr in self.TEAM_ABBR_MAP.keys():
            if abbr in text_content:
                found_teams.append(abbr)

        if len(found_teams) < 2:
            logger.debug(f"Table doesn't have 2 teams, found: {found_teams}")
            return lineups

        # Use first two teams found
        team1_abbr = found_teams[0]
        team2_abbr = found_teams[1]
        team1_name = self.TEAM_ABBR_MAP.get(team1_abbr, team1_abbr)
        team2_name = self.TEAM_ABBR_MAP.get(team2_abbr, team2_abbr)

        logger.debug(f"Parsing Basketball Monster table: {team1_name} vs {team2_name}")

        current_team = None

        for row in rows:
            try:
                row_text = row.get_text().strip()

                # Check if this row contains team header
                if team1_abbr in row_text and current_team != team1_name:
                    current_team = team1_name
                    continue
                elif team2_abbr in row_text and current_team != team2_name:
                    current_team = team2_name
                    continue

                if not current_team:
                    continue

                # Parse player data from cells
                cells = row.find_all(["td", "th"])

                if len(cells) < 2:
                    continue

                player_data = self._extract_player_data_from_cells(cells)

                if player_data:
                    lineups.append({
                        "scrape_date": scrape_date,
                        "game_date": game_date,
                        "team_name": current_team,
                        "player_name": player_data["name"],
                        "position": player_data.get("position"),
                        "status": player_data.get("status", "Active"),
                        "injury_description": player_data.get("injury_description"),
                        "notes": None,
                    })

                    logger.debug(
                        f"Found player: {player_data['name']} ({player_data.get('position')}) "
                        f"- {player_data.get('status', 'Active')} for {current_team}"
                    )

            except Exception as e:
                logger.debug(f"Failed to parse row: {e}")
                continue

        return lineups

    def _parse_game_container(
        self, container: Any, scrape_date: date, game_date: date
    ) -> List[Dict[str, Any]]:
        """Parse a game container div for lineup data.

        Args:
            container: BeautifulSoup div element containing game data
            scrape_date: Date when data was scraped
            game_date: Date of the game

        Returns:
            List of lineup entry dictionaries
        """
        lineups = []

        # Try to find team sections within the container
        team_divs = container.find_all(["div", "section"], recursive=True)

        for team_div in team_divs:
            try:
                text_content = team_div.get_text()

                # Find team
                team_name = None
                for abbr, full_name in self.TEAM_ABBR_MAP.items():
                    if abbr in text_content or full_name in text_content:
                        team_name = full_name
                        break

                if not team_name:
                    continue

                # Find player rows/elements
                player_elements = team_div.find_all(["li", "div", "tr"], class_=lambda x: x and any(
                    keyword in str(x).lower() for keyword in ["player", "lineup", "roster"]
                ))

                for element in player_elements:
                    player_data = self._extract_player_data_from_element(element)

                    if player_data:
                        lineups.append({
                            "scrape_date": scrape_date,
                            "game_date": game_date,
                            "team_name": team_name,
                            "player_name": player_data["name"],
                            "position": player_data.get("position"),
                            "status": player_data.get("status", "Active"),
                            "injury_description": player_data.get("injury_description"),
                            "notes": None,
                        })

            except Exception as e:
                logger.debug(f"Failed to parse team div: {e}")
                continue

        return lineups

    def _extract_player_data_from_cells(self, cells: List[Any]) -> Optional[Dict[str, Any]]:
        """Extract player data from table cells.

        Args:
            cells: List of BeautifulSoup cell elements

        Returns:
            Dictionary with player data or None
        """
        player_data = {}

        for i, cell in enumerate(cells):
            cell_text = cell.get_text().strip()

            if not cell_text or cell_text == "-":
                continue

            # First cell is usually player name
            if i == 0 and len(cell_text) > 2 and not cell_text.isdigit():
                # Check if it's not a position or status
                if cell_text.upper() not in ["PG", "SG", "SF", "PF", "C", "G", "F", "OUT", "GTD", "INJ", "Q", "D", "P"]:
                    player_data["name"] = cell_text

            # Check for position
            if cell_text.upper() in ["PG", "SG", "SF", "PF", "C", "G", "F"]:
                player_data["position"] = cell_text.upper()

            # Check for status indicators
            status_keywords = ["OUT", "GTD", "INJ", "Q", "D", "P", "QUESTIONABLE", "DOUBTFUL", "PROBABLE", "DTD"]
            if any(keyword in cell_text.upper() for keyword in status_keywords):
                player_data["status"] = self._normalize_status(cell_text.upper())
                player_data["injury_description"] = cell_text

        return player_data if "name" in player_data else None

    def _extract_player_data_from_element(self, element: Any) -> Optional[Dict[str, Any]]:
        """Extract player data from a div/li element.

        Args:
            element: BeautifulSoup element containing player data

        Returns:
            Dictionary with player data or None
        """
        player_data = {}
        text_content = element.get_text().strip()

        # Try to find player name (usually the main text or in a specific tag)
        name_elem = element.find(["a", "span"], class_=lambda x: x and "name" in str(x).lower())
        if name_elem:
            player_data["name"] = name_elem.get_text().strip()
        else:
            # Extract from text (usually first part before position/status)
            parts = text_content.split()
            if len(parts) >= 2:
                # Assume first 2-3 words are the name
                player_data["name"] = " ".join(parts[:2])

        # Find position
        pos_elem = element.find(["span", "div"], class_=lambda x: x and "pos" in str(x).lower())
        if pos_elem:
            pos_text = pos_elem.get_text().strip().upper()
            if pos_text in ["PG", "SG", "SF", "PF", "C", "G", "F"]:
                player_data["position"] = pos_text

        # Find status
        status_elem = element.find(["span", "div"], class_=lambda x: x and any(
            keyword in str(x).lower() for keyword in ["status", "injury", "inj"]
        ))
        if status_elem:
            status_text = status_elem.get_text().strip()
            player_data["status"] = self._normalize_status(status_text.upper())
            player_data["injury_description"] = status_text

        return player_data if "name" in player_data else None

    def _normalize_status(self, status: str) -> str:
        """Normalize status codes to standard format.

        Args:
            status: Raw status code

        Returns:
            Normalized status string
        """
        status_map = {
            "OUT": "OUT",
            "O": "OUT",
            "INJ": "OUT",
            "GTD": "GTD",
            "Q": "Questionable",
            "QUES": "Questionable",
            "D": "Doubtful",
            "DOUBT": "Doubtful",
            "P": "Probable",
            "PROB": "Probable",
            "DTD": "GTD",  # Day-to-day
        }

        return status_map.get(status.upper(), status)
