"""Statistical calculations for team performance."""

from datetime import date, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from nba_predictor.core.logger import get_logger
from nba_predictor.models import Game, TeamHistory, get_db

logger = get_logger(__name__)


class StatisticsCalculator:
    """Calculate team statistics and historical data."""

    def __init__(self) -> None:
        """Initialize statistics calculator."""
        logger.info("Statistics calculator initialized")

    def generate_team_statistics(self, season: str) -> int:
        """Generate team statistics for a season.

        Creates records for ALL teams for EVERY game date in the season,
        allowing simple date-based queries to compare all teams.

        Args:
            season: NBA season year

        Returns:
            Number of team history records generated
        """
        logger.info("Generating team statistics", season=season)

        with get_db() as db:
            # Delete existing statistics
            deleted = db.query(TeamHistory).filter(TeamHistory.season == season).delete()
            logger.info("Deleted existing statistics", count=deleted)

            # Get all unique game dates in the season
            game_dates = (
                db.query(Game.date)
                .distinct()
                .filter(Game.season == season, Game.home_point.isnot(None))
                .order_by(Game.date)
                .all()
            )

            if not game_dates:
                logger.warning("No games found for season", season=season)
                return 0

            # Get all teams
            teams = db.query(Game.home_name).distinct().filter(Game.season == season).all()

            records_created = 0

            # For each date, create records for ALL teams
            for (game_date,) in game_dates:
                logger.debug("Processing date", date=game_date, teams=len(teams))

                for (team_name,) in teams:
                    self._create_team_history_record(db, team_name, game_date, season)
                    records_created += 1

            logger.info("Team statistics generated", records=records_created, dates=len(game_dates), teams=len(teams))
            return records_created

    def _get_team_games(self, db: Session, team_name: str, season: str) -> List[Game]:
        """Get all games for a team in a season.

        Args:
            db: Database session
            team_name: Team name
            season: Season year

        Returns:
            List of games
        """
        return (
            db.query(Game)
            .filter(
                or_(Game.home_name == team_name, Game.away_name == team_name),
                Game.season == season,
                Game.home_point.isnot(None),
            )
            .order_by(Game.date)
            .all()
        )

    def _create_team_history_record(
        self, db: Session, team_name: str, game_date: date, season: str
    ) -> None:
        """Create or update team history record for a specific date.

        Args:
            db: Database session
            team_name: Team name
            game_date: Game date
            season: Season year
        """
        # Get previous games
        previous_games = (
            db.query(Game)
            .filter(
                or_(Game.home_name == team_name, Game.away_name == team_name),
                Game.date < game_date,
                Game.season == season,
                Game.home_point.isnot(None),
            )
            .order_by(Game.date.desc())
            .limit(10)
            .all()
        )

        if not previous_games:
            # First game of season
            history = TeamHistory(
                team_name=team_name,
                date=game_date,
                season=season,
                game=0,
                win=0,
            )
            db.add(history)
            return

        # Calculate statistics
        stats = self._calculate_statistics(team_name, previous_games)

        # Get day difference
        day_diff = (game_date - previous_games[0].date).days

        # Create history record
        history = TeamHistory(
            team_name=team_name,
            date=game_date,
            season=season,
            day_diff=day_diff,
            **stats,
        )

        db.add(history)

    def _calculate_statistics(self, team_name: str, games: List[Game]) -> dict:
        """Calculate statistics from previous games.

        Args:
            team_name: Team name
            games: List of previous games (most recent first)

        Returns:
            Dictionary of statistics
        """
        stats = {
            "game": len(games),
            "win": 0,
            "last1": 0,
            "last3": 0,
            "last5": 0,
            "last10": 0,
        }

        # Calculate for different windows
        total_points = 0
        total_points_against = 0
        total_wins = 0

        # Advanced metrics
        total_pace = Decimal(0)
        total_efg = Decimal(0)
        total_tov = Decimal(0)
        total_orb = Decimal(0)
        total_ftfga = Decimal(0)
        total_ortg = Decimal(0)

        # Quarter points - count only games where quarter data exists
        total_p1 = 0
        total_p2 = 0
        total_p3 = 0
        total_p4 = 0
        games_with_quarter_data = 0

        for i, game in enumerate(games):
            is_home = game.home_name == team_name
            team_points = game.home_point if is_home else game.away_point
            opp_points = game.away_point if is_home else game.home_point

            won = team_points > opp_points

            total_points += team_points
            total_points_against += opp_points
            if won:
                total_wins += 1

            # Window-specific stats
            if i == 0:
                stats["last1"] = 1 if won else 0
                stats["pointavg1"] = Decimal(team_points)
                stats["pointavg1a"] = Decimal(opp_points)
            if i < 3:
                if i == 2:
                    stats["last3"] = sum(
                        1
                        for g in games[:3]
                        if (
                            (g.home_name == team_name and g.home_point > g.away_point)
                            or (g.away_name == team_name and g.away_point > g.home_point)
                        )
                    )
                    stats["pointavg3"] = Decimal(
                        sum(
                            g.home_point if g.home_name == team_name else g.away_point
                            for g in games[:3]
                        )
                        / 3
                    )
            if i < 5:
                if i == 4:
                    stats["last5"] = sum(
                        1
                        for g in games[:5]
                        if (
                            (g.home_name == team_name and g.home_point > g.away_point)
                            or (g.away_name == team_name and g.away_point > g.home_point)
                        )
                    )
                    stats["pointavg5"] = Decimal(
                        sum(
                            g.home_point if g.home_name == team_name else g.away_point
                            for g in games[:5]
                        )
                        / 5
                    )
            if i < 10:
                if i == 9:
                    stats["last10"] = sum(
                        1
                        for g in games[:10]
                        if (
                            (g.home_name == team_name and g.home_point > g.away_point)
                            or (g.away_name == team_name and g.away_point > g.home_point)
                        )
                    )
                    stats["pointavg10"] = Decimal(
                        sum(
                            g.home_point if g.home_name == team_name else g.away_point
                            for g in games[:10]
                        )
                        / 10
                    )

            # Advanced metrics
            if is_home:
                if game.home_pace:
                    total_pace += game.home_pace
                if game.home_efg:
                    total_efg += game.home_efg
                if game.home_tov:
                    total_tov += game.home_tov
                if game.home_orb:
                    total_orb += game.home_orb
                if game.home_ftfga:
                    total_ftfga += game.home_ftfga
                if game.home_ortg:
                    total_ortg += game.home_ortg

                # Quarter points - only count if data exists
                if game.home_p1 is not None and game.home_p2 is not None and game.home_p3 is not None and game.home_p4 is not None:
                    total_p1 += game.home_p1
                    total_p2 += game.home_p2
                    total_p3 += game.home_p3
                    total_p4 += game.home_p4
                    games_with_quarter_data += 1
            else:
                if game.away_pace:
                    total_pace += game.away_pace
                if game.away_efg:
                    total_efg += game.away_efg
                if game.away_tov:
                    total_tov += game.away_tov
                if game.away_orb:
                    total_orb += game.away_orb
                if game.away_ftfga:
                    total_ftfga += game.away_ftfga
                if game.away_ortg:
                    total_ortg += game.away_ortg

                # Quarter points - only count if data exists
                if game.away_p1 is not None and game.away_p2 is not None and game.away_p3 is not None and game.away_p4 is not None:
                    total_p1 += game.away_p1
                    total_p2 += game.away_p2
                    total_p3 += game.away_p3
                    total_p4 += game.away_p4
                    games_with_quarter_data += 1

        # Calculate averages
        num_games = len(games)
        stats["win"] = total_wins
        stats["pointavg"] = Decimal(total_points) / Decimal(num_games)
        stats["pointavga"] = Decimal(total_points_against) / Decimal(num_games)

        stats["pace_avg"] = total_pace / Decimal(num_games)
        stats["efg_avg"] = total_efg / Decimal(num_games)
        stats["tov_avg"] = total_tov / Decimal(num_games)
        stats["orb_avg"] = total_orb / Decimal(num_games)
        stats["ftfga_avg"] = total_ftfga / Decimal(num_games)
        stats["ortg_avg"] = total_ortg / Decimal(num_games)

        # Calculate quarter averages only from games that have quarter data
        if games_with_quarter_data > 0:
            stats["p1_avg"] = Decimal(total_p1) / Decimal(games_with_quarter_data)
            stats["p2_avg"] = Decimal(total_p2) / Decimal(games_with_quarter_data)
            stats["p3_avg"] = Decimal(total_p3) / Decimal(games_with_quarter_data)
            stats["p4_avg"] = Decimal(total_p4) / Decimal(games_with_quarter_data)

        return stats

    def calculate_streaks(self, season: str) -> int:
        """Calculate win/loss streaks for teams.

        Args:
            season: NBA season year

        Returns:
            Number of records updated
        """
        logger.info("Calculating streaks", season=season)

        with get_db() as db:
            teams = db.query(TeamHistory.team_name).distinct().filter(TeamHistory.season == season).all()

            records_updated = 0

            for (team_name,) in teams:
                history_records = (
                    db.query(TeamHistory)
                    .filter(TeamHistory.team_name == team_name, TeamHistory.season == season)
                    .order_by(TeamHistory.date)
                    .all()
                )

                win_streak = 0
                loss_streak = 0
                prev_wins = 0

                for record in history_records:
                    if record.win and record.win > prev_wins:
                        win_streak += 1
                        loss_streak = 0
                    else:
                        win_streak = 0
                        loss_streak += 1

                    record.win_streak = win_streak
                    record.loss_streak = loss_streak
                    prev_wins = record.win or 0
                    records_updated += 1

            logger.info("Streaks calculated", records=records_updated)
            return records_updated
