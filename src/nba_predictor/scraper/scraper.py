"""Modern NBA scraper with robust error handling and retry logic."""

import time
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import cloudscraper  # <-- Trocar requests por cloudscraper
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from sqlalchemy import func
from urllib3.util.retry import Retry

from nba_predictor.core.config import get_settings
from nba_predictor.core.logger import get_logger
from nba_predictor.models import Game, PlayByPlay, get_db

logger = get_logger(__name__)


class ScraperError(Exception):
    """Base exception for scraper errors."""

    pass


class BasketballReferenceScraper:
    """Scraper for Basketball Reference website."""

    MONTH_MAP = {
        "october": 10,
        "november": 11,
        "december": 12,
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
    }

    def _establish_session(self) -> None:
        """Establish a session by visiting the homepage first."""
        try:
            # Visit homepage first to get cookies
            homepage_response = self.session.get(
                self.base_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                },
                timeout=30
            )
            logger.info("Session established", status=homepage_response.status_code)
            time.sleep(2)  # Wait before making actual requests
        except Exception as e:
            logger.warning("Could not establish session", error=str(e))

    def __init__(self) -> None:
        """Initialize the scraper with configuration."""
        self.settings = get_settings()
        self.base_url = self.settings.scraper.base_url
        self.session = self._create_session()
        self._establish_session()  # <-- Adicione esta linha
        logger.info("Basketball Reference scraper initialized")

    def _create_session(self) -> cloudscraper.CloudScraper:
        """Create a cloudscraper session with retry logic.

        Returns:
            Configured cloudscraper session
        """
        # Use cloudscraper instead of requests.Session
        session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'darwin',
                'desktop': True
            }
        )
        
        return session

    def _get_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a page with error handling.

        Args:
            url: URL to fetch

        Returns:
            Parsed BeautifulSoup object

        Raises:
            ScraperError: If request fails
        """
        try:
            logger.debug("Fetching page", url=url)
            
            # Add small random delay to avoid rate limiting
            time.sleep(1.5 + (hash(url) % 100) / 100)
            
            # Override headers for this specific request to match working curl
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.basketball-reference.com/',
                'Connection': 'keep-alive',
            }
            
            response = self.session.get(
                url, 
                headers=headers, 
                timeout=self.settings.scraper.timeout,
                allow_redirects=True
            )
            response.raise_for_status()

            return BeautifulSoup(response.text, "html.parser")

        except requests.exceptions.Timeout:
            logger.error("Request timeout", url=url)
            raise ScraperError(f"Timeout fetching {url}")

        except requests.exceptions.HTTPError as e:
            logger.error("HTTP error", url=url, status_code=e.response.status_code)
            raise ScraperError(f"HTTP error {e.response.status_code} for {url}")

        except requests.exceptions.RequestException as e:
            logger.error("Request failed", url=url, error=str(e))
            raise ScraperError(f"Failed to fetch {url}: {e}")

    def import_games(self, season: str, month: str) -> int:
        """Import games for a specific season and month.

        Args:
            season: NBA season year (e.g., "2024")
            month: Month name (e.g., "january")

        Returns:
            Number of games imported

        Raises:
            ValueError: If month is invalid
            ScraperError: If scraping fails
        """
        if month.lower() not in self.MONTH_MAP:
            raise ValueError(f"Invalid month: {month}")

        month_lower = month.lower()
        month_num = self.MONTH_MAP[month_lower]

        logger.info("Starting game import", season=season, month=month, month_num=month_num)

        # Delete existing games for this period
        with get_db() as db:
            deleted = (
                db.query(Game)
                .filter(Game.season == season)
                .filter(func.month(Game.date) == month_num)
                .delete(synchronize_session=False)
            )
            logger.info("Deleted existing games", count=deleted)

        # Fetch schedule page
        schedule_url = f"{self.base_url}/leagues/NBA_{season}_games-{month_lower}.html"
        schedule_page = self._get_page(schedule_url)

        table = schedule_page.find("table")
        if not table:
            logger.warning("No games table found", url=schedule_url)
            return 0

        games_imported = 0

        for row in table.find_all("tr")[1:]:  # Skip header row
            columns = row.find_all("td")
            date_column = row.find_all("th")

            if not columns:
                continue

            try:
                game_data = self._extract_game_data(
                    columns, date_column, season, month_num, month_lower
                )

                if game_data:
                    with get_db() as db:
                        game = Game(**game_data)
                        db.add(game)
                        games_imported += 1

                    logger.info(
                        "Imported game",
                        date=game_data["date"],
                        home=game_data["home_name"],
                        away=game_data["away_name"],
                    )

                    # Rate limiting
                    time.sleep(0.5)

            except Exception as e:
                logger.error("Failed to import game", error=str(e), exc_info=True)
                continue

        logger.info("Game import completed", games_imported=games_imported)
        return games_imported

    def _extract_game_data(
        self,
        columns: List[Any],
        date_column: List[Any],
        season: str,
        month_num: int,
        month: str,
    ) -> Optional[Dict[str, Any]]:
        """Extract game data from HTML row.

        Args:
            columns: Table columns
            date_column: Date column
            season: Season year
            month_num: Month number
            month: Month name

        Returns:
            Dictionary of game data or None if incomplete
        """
        game_data: Dict[str, Any] = {
            "season": season,
        }

        # Extract basic info
        if not columns[5].text:
            # Future game without results
            game_data.update(
                {
                    "home_name": columns[3].text,
                    "away_name": columns[1].text,
                    "date": self._parse_date(date_column[0].text, month_num),
                }
            )
            return game_data

        # Extract game ID and scores
        game_link = columns[5].find("a")
        if not game_link:
            return None

        game_id = game_link["href"].split("/boxscores/")[1].replace(".html", "")

        game_data.update(
            {
                "id2": game_id,
                "home_name": columns[3].text.strip(),
                "away_name": columns[1].text.strip(),
                "home_point": int(columns[4].text) if columns[4].text else None,
                "away_point": int(columns[2].text) if columns[2].text else None,
                "date": self._parse_date(date_column[0].text, month_num),
                "overtime": columns[6].text if columns[6].text else None,
            }
        )

        # Fetch detailed game stats
        try:
            detailed_stats = self._fetch_game_details(game_id)
            game_data.update(detailed_stats)
        except ScraperError as e:
            logger.warning("Could not fetch game details", game_id=game_id, error=str(e))

        return game_data

    def _parse_date(self, date_text: str, month_num: int) -> date:
        """Parse date from Basketball Reference format.

        Args:
            date_text: Date text (e.g., "Tue, Jan 7, 2017")
            month_num: Month number

        Returns:
            Parsed date object
        """
        parts = date_text.split(", ")
        day = int(parts[1].split()[1])
        year = int(parts[2])

        return date(year, month_num, day)

    def _fetch_game_details(self, game_id: str) -> Dict[str, Any]:
        """Fetch detailed statistics for a game.

        Args:
            game_id: Game ID

        Returns:
            Dictionary of detailed game statistics
        """
        game_url = f"{self.base_url}/boxscores/{game_id}.html"
        game_page = self._get_page(game_url)

        details: Dict[str, Any] = {}

        # Extract line score (quarter scores)
        line_score_div = game_page.find("div", {"id": "all_line_score"})
        if line_score_div:
            line_score = self._extract_from_comment(line_score_div)
            if line_score:
                details.update(self._parse_line_score(line_score))

        # Extract four factors (advanced stats)
        four_factors_div = game_page.find("div", {"id": "all_four_factors"})
        if four_factors_div:
            four_factors = self._extract_from_comment(four_factors_div)
            if four_factors:
                details.update(self._parse_four_factors(four_factors))

        return details

    def _extract_from_comment(self, div: Any) -> Optional[BeautifulSoup]:
        """Extract HTML from commented sections.

        Args:
            div: BeautifulSoup div element

        Returns:
            Parsed content or None
        """
        html_str = str(div)
        html_str = html_str.replace("<!--", "").replace("-->", "")
        return BeautifulSoup(html_str, "lxml")

    def _parse_line_score(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Parse quarter scores from line score table.

        Args:
            soup: Parsed line score HTML

        Returns:
            Dictionary with quarter scores
        """
        scores: Dict[str, int] = {}

        rows = soup.find_all("tr")[2:]  # Skip header rows
        if len(rows) >= 2:
            away_row = rows[0].find_all("td")
            home_row = rows[1].find_all("td")

            if len(away_row) >= 5 and len(home_row) >= 5:
                scores.update(
                    {
                        "away_p1": int(away_row[1].text),
                        "away_p2": int(away_row[2].text),
                        "away_p3": int(away_row[3].text),
                        "away_p4": int(away_row[4].text),
                        "home_p1": int(home_row[1].text),
                        "home_p2": int(home_row[2].text),
                        "home_p3": int(home_row[3].text),
                        "home_p4": int(home_row[4].text),
                    }
                )

        return scores

    def _parse_four_factors(self, soup: BeautifulSoup) -> Dict[str, float]:
        """Parse advanced stats from four factors table.

        Args:
            soup: Parsed four factors HTML

        Returns:
            Dictionary with advanced statistics
        """
        stats: Dict[str, float] = {}

        rows = soup.find_all("tr")[2:]  # Skip header rows
        if len(rows) >= 2:
            away_row = rows[0].find_all("td")
            home_row = rows[1].find_all("td")

            if len(away_row) >= 6 and len(home_row) >= 6:
                stats.update(
                    {
                        "away_pace": float(away_row[0].text),
                        "away_efg": float(away_row[1].text),
                        "away_tov": float(away_row[2].text),
                        "away_orb": float(away_row[3].text),
                        "away_ftfga": float(away_row[4].text),
                        "away_ortg": float(away_row[5].text),
                        "home_pace": float(home_row[0].text),
                        "home_efg": float(home_row[1].text),
                        "home_tov": float(home_row[2].text),
                        "home_orb": float(home_row[3].text),
                        "home_ftfga": float(home_row[4].text),
                        "home_ortg": float(home_row[5].text),
                    }
                )

        return stats

    def import_play_by_play(self, game_date: date) -> int:
        """Import play-by-play data for games on a specific date.

        Args:
            game_date: Date to import play-by-play data for

        Returns:
            Number of games processed

        Raises:
            ScraperError: If scraping fails
        """
        logger.info("Starting play-by-play import", date=game_date)

        # Delete existing play-by-play data
        with get_db() as db:
            game_ids = (
                db.query(Game.id2).filter(Game.date == game_date).filter(Game.id2.isnot(None)).all()
            )

            for (game_id,) in game_ids:
                db.query(PlayByPlay).filter(PlayByPlay.game_id == game_id).delete(
                    synchronize_session=False
                )

            logger.info("Deleted existing play-by-play data", games=len(game_ids))

        games_processed = 0

        for (game_id,) in game_ids:
            try:
                self._import_game_play_by_play(game_id)
                games_processed += 1
                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                logger.error("Failed to import play-by-play", game_id=game_id, error=str(e))
                continue

        logger.info("Play-by-play import completed", games_processed=games_processed)
        return games_processed

    def _import_game_play_by_play(self, game_id: str) -> None:
        """Import play-by-play data for a specific game.

        Args:
            game_id: Game ID

        Raises:
            ScraperError: If scraping fails
        """
        pbp_url = f"{self.base_url}/boxscores/pbp/{game_id}.html"
        pbp_page = self._get_page(pbp_url)

        table = pbp_page.find("table", {"id": "pbp"})
        if not table:
            logger.warning("No play-by-play table found", game_id=game_id)
            return

        current_quarter = 1

        for row in table.find_all("tr"):
            # Check for quarter markers
            row_id = row.get("id")
            if row_id and row_id.startswith("q"):
                quarter_num = row_id[1:]
                if quarter_num.isdigit():
                    current_quarter = int(quarter_num)

            columns = row.find_all("td")
            if not columns or len(columns) < 6:
                continue

            try:
                play_data = self._extract_play_data(columns, game_id, current_quarter)
                if play_data:
                    with get_db() as db:
                        play = PlayByPlay(**play_data)
                        db.add(play)

            except Exception as e:
                logger.debug("Failed to parse play", error=str(e))
                continue

    def _extract_play_data(
        self, columns: List[Any], game_id: str, quarter: int
    ) -> Optional[Dict[str, Any]]:
        """Extract play-by-play data from HTML row.

        Args:
            columns: Table columns
            game_id: Game ID
            quarter: Current quarter

        Returns:
            Dictionary of play data or None if invalid
        """
        if not columns[0].text:
            return None

        try:
            # Parse time (MM:SS format)
            time_parts = columns[0].text.strip().split(":")
            minutes = int(time_parts[0])
            seconds = int(time_parts[1])
            duration = 720 - (minutes * 60 + seconds)  # Convert to seconds elapsed

            return {
                "game_id": game_id,
                "quarter": str(quarter),
                "duration": duration,
                "away_comment": columns[1].text.strip() if columns[1].text else None,
                "away_score": int(columns[2].text) if columns[2].text else None,
                "home_score": int(columns[4].text) if columns[4].text else None,
                "home_comment": columns[5].text.strip() if columns[5].text else None,
            }

        except (ValueError, IndexError):
            return None
