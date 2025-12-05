"""Image-based NBA lineup scraper using Anthropic Vision API.

This scraper reads screenshots of lineup pages (like RotoWire or Basketball Monster)
and uses Claude's vision capabilities to extract structured lineup data.
"""

import base64
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import anthropic
from sqlalchemy import and_

from nba_predictor.core.config import get_settings
from nba_predictor.core.logger import get_logger
from nba_predictor.models import DailyLineup, get_db

logger = get_logger(__name__)


class ImageLineupScraperError(Exception):
    """Base exception for image lineup scraper errors."""

    pass


class ImageLineupScraper:
    """Scraper that reads lineup data from images using Claude Vision API."""

    # Mapping of team abbreviations to full names
    TEAM_ABBR_MAP = {
        "ATL": "Atlanta Hawks",
        "BOS": "Boston Celtics",
        "BKN": "Brooklyn Nets",
        "BRK": "Brooklyn Nets",
        "CHA": "Charlotte Hornets",
        "CHO": "Charlotte Hornets",
        "CHI": "Chicago Bulls",
        "CLE": "Cleveland Cavaliers",
        "DAL": "Dallas Mavericks",
        "DEN": "Denver Nuggets",
        "DET": "Detroit Pistons",
        "GSW": "Golden State Warriors",
        "GS": "Golden State Warriors",
        "HOU": "Houston Rockets",
        "IND": "Indiana Pacers",
        "LAC": "Los Angeles Clippers",
        "LAL": "Los Angeles Lakers",
        "LA": "Los Angeles Lakers",
        "MEM": "Memphis Grizzlies",
        "MIA": "Miami Heat",
        "MIL": "Milwaukee Bucks",
        "MIN": "Minnesota Timberwolves",
        "NOP": "New Orleans Pelicans",
        "NO": "New Orleans Pelicans",
        "NYK": "New York Knicks",
        "NY": "New York Knicks",
        "OKC": "Oklahoma City Thunder",
        "ORL": "Orlando Magic",
        "PHI": "Philadelphia 76ers",
        "PHX": "Phoenix Suns",
        "POR": "Portland Trail Blazers",
        "SAC": "Sacramento Kings",
        "SAS": "San Antonio Spurs",
        "SA": "San Antonio Spurs",
        "TOR": "Toronto Raptors",
        "UTA": "Utah Jazz",
        "WAS": "Washington Wizards",
    }

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize the scraper with Anthropic API.

        Args:
            api_key: Anthropic API key (if not provided, will look for ANTHROPIC_API_KEY env var)
        """
        self.settings = get_settings()
        self.client = anthropic.Anthropic(api_key=api_key)
        logger.info("Image lineup scraper initialized")

    def _encode_image(self, image_path: Union[str, Path]) -> tuple[str, str]:
        """Encode an image file to base64.

        Args:
            image_path: Path to image file

        Returns:
            Tuple of (base64_data, media_type)

        Raises:
            ImageLineupScraperError: If image cannot be read
        """
        try:
            image_path = Path(image_path)

            if not image_path.exists():
                raise ImageLineupScraperError(f"Image file not found: {image_path}")

            # Determine media type from extension
            ext = image_path.suffix.lower()
            media_type_map = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".webp": "image/webp",
            }

            media_type = media_type_map.get(ext, "image/jpeg")

            # Read and encode image
            with open(image_path, "rb") as f:
                image_data = base64.standard_b64encode(f.read()).decode("utf-8")

            logger.debug("Image encoded", path=str(image_path), media_type=media_type)
            return image_data, media_type

        except Exception as e:
            logger.error("Failed to encode image", path=str(image_path), error=str(e))
            raise ImageLineupScraperError(f"Failed to encode image: {e}")

    def _extract_lineups_from_image(self, image_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """Extract lineup data from an image using Claude Vision.

        Args:
            image_path: Path to lineup image (screenshot)

        Returns:
            List of lineup dictionaries

        Raises:
            ImageLineupScraperError: If extraction fails
        """
        try:
            logger.info("Extracting lineups from image", path=str(image_path))

            # Encode image
            image_data, media_type = self._encode_image(image_path)

            # Create the prompt for Claude
            prompt = """You are analyzing a screenshot of NBA daily lineups. Please extract ALL the lineup information from this image.

For each game shown in the image, extract:
1. Both team names (full names like "Los Angeles Lakers" or abbreviations like "LAL")
2. For each team, list ALL players in the expected lineup
3. For each player, provide:
   - Player name (first and last name)
   - Position (PG, SG, SF, PF, C, G, or F)
   - Status (one of: "Starter", "Expected Lineup", "OUT", "Doubtful", "Questionable", "GTD", "Probable", or "Active")
   - Injury description (if any injury label is shown like "Out", "Doubtful", "GTD", etc.)

Return the data as a JSON array with this exact structure:
[
  {
    "team_name": "Los Angeles Lakers",
    "player_name": "LeBron James",
    "position": "SF",
    "status": "Starter",
    "injury_description": null
  },
  {
    "team_name": "Boston Celtics",
    "player_name": "Jayson Tatum",
    "position": "SF",
    "status": "OUT",
    "injury_description": "Out"
  }
]

IMPORTANT:
- For team names, if you see an abbreviation, convert it to the full team name. For example: "LAL" → "Los Angeles Lakers", "BOS" → "Boston Celtics"
- Include ALL players shown in the lineup, not just starters
- If a player is in the "Expected Lineup" section, use status "Expected Lineup"
- If a player has an injury indicator (Out, Doubtful, Questionable, GTD, etc.), use that as the status
- If a player has an injury status but no injury description is visible, set injury_description to the status value
- Only return the JSON array, no other text or explanation"""

            # Call Claude Vision API
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt,
                            },
                        ],
                    }
                ],
            )

            # Extract response text
            response_text = message.content[0].text
            logger.debug("Claude Vision response received", length=len(response_text))

            # Parse JSON response
            # Claude might wrap the JSON in markdown code blocks, so let's handle that
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            lineups = json.loads(response_text)

            logger.info("Successfully extracted lineups", count=len(lineups))
            return lineups

        except json.JSONDecodeError as e:
            logger.error("Failed to parse Claude response as JSON", error=str(e), response=response_text[:500])
            raise ImageLineupScraperError(f"Failed to parse response as JSON: {e}")
        except Exception as e:
            logger.error("Failed to extract lineups from image", error=str(e), exc_info=True)
            raise ImageLineupScraperError(f"Failed to extract lineups: {e}")

    def _normalize_team_name(self, team_identifier: str) -> str:
        """Convert team abbreviation or name to full standardized name.

        Args:
            team_identifier: Team abbreviation or partial name

        Returns:
            Full standardized team name
        """
        # First try direct abbreviation lookup
        if team_identifier.upper() in self.TEAM_ABBR_MAP:
            return self.TEAM_ABBR_MAP[team_identifier.upper()]

        # Try to match against known full names
        team_identifier_lower = team_identifier.lower()
        for abbr, full_name in self.TEAM_ABBR_MAP.items():
            if team_identifier_lower in full_name.lower() or full_name.lower() in team_identifier_lower:
                return full_name

        # Return as-is if no match found
        logger.warning("Could not normalize team name", team=team_identifier)
        return team_identifier

    def import_lineups_from_image(
        self,
        image_path: Union[str, Path],
        game_date: Optional[date] = None,
    ) -> int:
        """Import lineups from an image screenshot.

        Args:
            image_path: Path to lineup screenshot
            game_date: Date of the game (defaults to today)

        Returns:
            Number of lineup entries imported

        Raises:
            ImageLineupScraperError: If import fails
        """
        if game_date is None:
            game_date = date.today()

        scrape_date = date.today()

        logger.info(
            "Starting lineup import from image",
            image=str(image_path),
            game_date=game_date,
            scrape_date=scrape_date,
        )

        # Extract lineups from image
        raw_lineups = self._extract_lineups_from_image(image_path)

        # Delete existing lineups for this scrape date and game date combination
        with get_db() as db:
            deleted = (
                db.query(DailyLineup)
                .filter(
                    and_(
                        DailyLineup.scrape_date == scrape_date,
                        DailyLineup.game_date == game_date,
                    )
                )
                .delete(synchronize_session=False)
            )
            logger.info("Deleted existing lineups", count=deleted)

        # Import lineups to database
        lineups_imported = 0

        for lineup_data in raw_lineups:
            try:
                # Normalize team name
                team_name = self._normalize_team_name(lineup_data["team_name"])

                # Prepare database entry
                db_entry = {
                    "scrape_date": scrape_date,
                    "game_date": game_date,
                    "team_name": team_name,
                    "player_name": lineup_data["player_name"],
                    "position": lineup_data.get("position"),
                    "status": lineup_data.get("status", "Active"),
                    "injury_description": lineup_data.get("injury_description"),
                    "notes": None,
                }

                # Save to database
                with get_db() as db:
                    lineup = DailyLineup(**db_entry)
                    db.add(lineup)
                    lineups_imported += 1

                logger.debug(
                    "Imported lineup entry",
                    team=team_name,
                    player=lineup_data["player_name"],
                    status=db_entry["status"],
                )

            except Exception as e:
                logger.error(
                    "Failed to import lineup entry",
                    lineup=lineup_data,
                    error=str(e),
                    exc_info=True,
                )
                continue

        logger.info("Lineup import completed", lineups_imported=lineups_imported)
        return lineups_imported

    def import_lineups_from_multiple_images(
        self,
        image_paths: List[Union[str, Path]],
        game_date: Optional[date] = None,
    ) -> int:
        """Import lineups from multiple image screenshots.

        Useful when you have multiple screenshots of different games.

        Args:
            image_paths: List of paths to lineup screenshots
            game_date: Date of the games (defaults to today)

        Returns:
            Total number of lineup entries imported
        """
        total_imported = 0

        for image_path in image_paths:
            try:
                count = self.import_lineups_from_image(image_path, game_date)
                total_imported += count
            except Exception as e:
                logger.error(
                    "Failed to import from image",
                    image=str(image_path),
                    error=str(e),
                )
                continue

        logger.info(
            "Completed multiple image import",
            images_processed=len(image_paths),
            total_imported=total_imported,
        )
        return total_imported
