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
from nba_predictor.models import Game, PlayByPlay, PlayerGameStats, get_db

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

                    # Import player stats if game has been played (has game_id)
                    if game_data.get("id2"):
                        try:
                            player_stats_count = self.import_player_stats(
                                game_data["id2"], game_data["date"], season
                            )
                            logger.info(
                                "Imported player stats",
                                game_id=game_data["id2"],
                                count=player_stats_count,
                            )
                        except Exception as e:
                            logger.warning(
                                "Failed to import player stats",
                                game_id=game_data.get("id2"),
                                error=str(e),
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

            if len(away_row) >= 4 and len(home_row) >= 4:
                scores.update(
                    {
                        "away_p1": int(away_row[0].text),
                        "away_p2": int(away_row[1].text),
                        "away_p3": int(away_row[2].text),
                        "away_p4": int(away_row[3].text),
                        "home_p1": int(home_row[0].text),
                        "home_p2": int(home_row[1].text),
                        "home_p3": int(home_row[2].text),
                        "home_p4": int(home_row[3].text),
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

    def import_play_by_play_for_month(self, season: str, month: str) -> int:
        """Import play-by-play data for all games in a specific season and month.

        Args:
            season: NBA season year (e.g., "2024")
            month: Month name (e.g., "january")

        Returns:
            Number of games processed

        Raises:
            ValueError: If month is invalid
            ScraperError: If scraping fails
        """
        if month.lower() not in self.MONTH_MAP:
            raise ValueError(f"Invalid month: {month}")

        month_num = self.MONTH_MAP[month.lower()]

        logger.info("Starting play-by-play import for month", season=season, month=month)

        # Get all games for this month
        with get_db() as db:
            game_ids = (
                db.query(Game.id2)
                .filter(Game.season == season)
                .filter(func.month(Game.date) == month_num)
                .filter(Game.id2.isnot(None))
                .all()
            )

            # Delete existing play-by-play data for these games
            for (game_id,) in game_ids:
                db.query(PlayByPlay).filter(PlayByPlay.game_id == game_id).delete(
                    synchronize_session=False
                )

            logger.info("Deleted existing play-by-play data for month", games=len(game_ids))

        games_processed = 0

        for (game_id,) in game_ids:
            try:
                self._import_game_play_by_play(game_id)
                games_processed += 1
                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                logger.error("Failed to import play-by-play", game_id=game_id, error=str(e))
                continue

        logger.info("Play-by-play import for month completed", games_processed=games_processed)
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

    def import_player_stats(self, game_id: str, game_date: date, season: str) -> int:
        """Import player statistics for a specific game.

        Args:
            game_id: Game ID
            game_date: Date of the game
            season: Season year

        Returns:
            Number of player stats imported

        Raises:
            ScraperError: If scraping fails
        """
        logger.info("Starting player stats import", game_id=game_id)

        # Delete existing player stats for this game
        with get_db() as db:
            deleted = (
                db.query(PlayerGameStats)
                .filter(PlayerGameStats.game_id == game_id)
                .delete(synchronize_session=False)
            )
            logger.debug("Deleted existing player stats", count=deleted, game_id=game_id)

        # Fetch box score page
        box_score_url = f"{self.base_url}/boxscores/{game_id}.html"
        box_score_page = self._get_page(box_score_url)

        stats_imported = 0

        # Get team names from the game
        with get_db() as db:
            game = db.query(Game).filter(Game.id2 == game_id).first()
            if not game:
                logger.warning("Game not found", game_id=game_id)
                return 0

            away_team = game.away_name
            home_team = game.home_name

        # Extract team abbreviations from the page for table IDs
        # Basketball Reference uses team abbreviations in table IDs (e.g., "box-LAL-game-basic")
        team_links = box_score_page.find_all("a", href=lambda x: x and "/teams/" in x)
        team_abbrevs = []
        for link in team_links[:2]:  # First two team links are the playing teams
            abbrev = link["href"].split("/teams/")[1].split("/")[0]
            team_abbrevs.append(abbrev)

        if len(team_abbrevs) != 2:
            logger.warning("Could not find team abbreviations", game_id=game_id)
            return 0

        # Process away team stats (first team)
        away_stats = self._parse_player_stats_table(
            box_score_page, team_abbrevs[0], away_team, game_id, game_date, season
        )
        for stat in away_stats:
            with get_db() as db:
                player_stat = PlayerGameStats(**stat)
                db.add(player_stat)
                stats_imported += 1

        # Process home team stats (second team)
        home_stats = self._parse_player_stats_table(
            box_score_page, team_abbrevs[1], home_team, game_id, game_date, season
        )
        for stat in home_stats:
            with get_db() as db:
                player_stat = PlayerGameStats(**stat)
                db.add(player_stat)
                stats_imported += 1

        logger.info("Player stats import completed", game_id=game_id, stats_imported=stats_imported)
        return stats_imported

    def _parse_player_stats_table(
        self,
        soup: BeautifulSoup,
        team_abbrev: str,
        team_name: str,
        game_id: str,
        game_date: date,
        season: str,
    ) -> List[Dict[str, Any]]:
        """Parse player statistics table for a team.

        Args:
            soup: Parsed box score HTML
            team_abbrev: Team abbreviation (e.g., "LAL")
            team_name: Full team name
            game_id: Game ID
            game_date: Date of the game
            season: Season year

        Returns:
            List of player statistics dictionaries
        """
        stats_list = []

        # Find the basic stats table for this team
        table_id = f"box-{team_abbrev}-game-basic"
        table = soup.find("table", {"id": table_id})

        if not table:
            logger.warning("Player stats table not found", team=team_name, table_id=table_id)
            return stats_list

        tbody = table.find("tbody")
        if not tbody:
            return stats_list

        is_starter = True  # First 5 players are starters

        for idx, row in enumerate(tbody.find_all("tr")):
            # Check if this is the "Reserves" row separator
            if row.get("class") and "thead" in row.get("class"):
                is_starter = False
                continue

            # Skip team total rows
            if row.get("class") and "full_table" not in row.get("class"):
                continue

            try:
                player_stat = self._extract_player_stat(
                    row, team_name, game_id, game_date, season, is_starter
                )
                if player_stat:
                    stats_list.append(player_stat)
            except Exception as e:
                logger.debug("Failed to parse player stat", error=str(e), team=team_name)
                continue

        return stats_list

    def _extract_player_stat(
        self,
        row: Any,
        team_name: str,
        game_id: str,
        game_date: date,
        season: str,
        is_starter: bool,
    ) -> Optional[Dict[str, Any]]:
        """Extract player statistics from HTML row.

        Args:
            row: BeautifulSoup row element
            team_name: Team name
            game_id: Game ID
            game_date: Date of the game
            season: Season year
            is_starter: Whether player is a starter

        Returns:
            Dictionary of player statistics or None if invalid
        """
        cells = row.find_all(["th", "td"])
        if len(cells) < 20:  # Basic box score has ~20 columns
            return None

        # Get player name from first cell
        player_link = cells[0].find("a")
        if not player_link:
            return None

        player_name = player_link.text.strip()

        # Check if player did not play (DNP)
        mp_cell = cells[1]  # Minutes Played
        if mp_cell.text.strip() in ["Did Not Play", "Did Not Dress", "Not With Team", ""]:
            return None

        try:
            # Helper function to safely get cell text as int
            def get_int(cell, default=0):
                text = cell.text.strip()
                return int(text) if text and text.isdigit() else default

            # Helper function to safely get cell text as float
            def get_float(cell, default=None):
                text = cell.text.strip()
                try:
                    return float(text) if text else default
                except ValueError:
                    return default

            # Extract statistics
            return {
                "game_id": game_id,
                "game_date": game_date,
                "season": season,
                "team_name": team_name,
                "player_name": player_name,
                "is_starter": is_starter,
                "minutes_played": cells[1].text.strip() or None,
                "field_goals": get_int(cells[2]),
                "field_goal_attempts": get_int(cells[3]),
                "field_goal_percentage": get_float(cells[4]),
                "three_pointers": get_int(cells[5]),
                "three_point_attempts": get_int(cells[6]),
                "three_point_percentage": get_float(cells[7]),
                "free_throws": get_int(cells[8]),
                "free_throw_attempts": get_int(cells[9]),
                "free_throw_percentage": get_float(cells[10]),
                "offensive_rebounds": get_int(cells[11]),
                "defensive_rebounds": get_int(cells[12]),
                "total_rebounds": get_int(cells[13]),
                "assists": get_int(cells[14]),
                "steals": get_int(cells[15]),
                "blocks": get_int(cells[16]),
                "turnovers": get_int(cells[17]),
                "personal_fouls": get_int(cells[18]),
                "points": get_int(cells[19]),
                "plus_minus": cells[20].text.strip() if len(cells) > 20 else None,
            }
        except (ValueError, IndexError) as e:
            logger.debug("Failed to extract player stat", error=str(e), player=player_name)
            return None
