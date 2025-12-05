"""Command-line interface for NBA Predictor."""

import sys
from datetime import date, datetime
from typing import List, Optional

from nba_predictor.core.config import get_settings
from nba_predictor.core.logger import get_logger, setup_logging
from nba_predictor.models import init_db, create_tables
from nba_predictor.prediction.claude_predictor import ClaudePredictor, PredictionError
from nba_predictor.scraper.scraper import BasketballReferenceScraper, ScraperError
from nba_predictor.scraper.rotowire_scraper import RotoWireScraper, RotoWireScraperError
from nba_predictor.utils.statistics import StatisticsCalculator

logger = get_logger(__name__)


class NBA_Predictor_CLI:
    """Command-line interface for NBA Predictor."""

    def __init__(self) -> None:
        """Initialize CLI."""
        setup_logging()
        self.settings = get_settings()
        init_db()

        self.scraper = BasketballReferenceScraper()
        self.rotowire_scraper = RotoWireScraper()
        self.stats_calculator = StatisticsCalculator()

    def init_database(self) -> None:
        """Initialize database tables."""
        print("🏀 Initializing database...")
        try:
            create_tables()
            print("✅ Database initialized successfully!")
        except Exception as e:
            print(f"❌ Failed to initialize database: {e}")
            logger.error("Database initialization failed", error=str(e), exc_info=True)
            sys.exit(1)

    def scrape_games(self, season: str, months: List[str], scrape_pbp: bool = False) -> None:
        """Scrape games for a season and one or more months.

        Args:
            season: NBA season year
            months: List of month names
            scrape_pbp: Whether to also scrape play-by-play data
        """
        total_games = 0
        total_pbp_games = 0

        for month in months:
            print(f"🏀 Scraping games for {month} {season}...")
            try:
                count = self.scraper.import_games(season, month)
                print(f"✅ Imported {count} games for {month}!")
                total_games += count

                # Scrape play-by-play if requested
                if scrape_pbp and count > 0:
                    print(f"🏀 Scraping play-by-play data for {month} {season}...")
                    pbp_count = self.scraper.import_play_by_play_for_month(season, month)
                    print(f"✅ Imported play-by-play for {pbp_count} games in {month}!")
                    total_pbp_games += pbp_count

            except (ScraperError, ValueError) as e:
                print(f"❌ Failed to scrape games for {month}: {e}")
                logger.error("Game scraping failed", month=month, error=str(e), exc_info=True)
                continue

        print(f"\n{'='*60}")
        print(f"📊 Summary:")
        print(f"   Total games imported: {total_games}")
        if scrape_pbp:
            print(f"   Total play-by-play games: {total_pbp_games}")
        print(f"{'='*60}\n")

    def scrape_play_by_play(self, date_str: str) -> None:
        """Scrape play-by-play data for a date.

        Args:
            date_str: Date in YYYY-MM-DD format
        """
        try:
            game_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            print(f"🏀 Scraping play-by-play for {game_date}...")

            count = self.scraper.import_play_by_play(game_date)
            print(f"✅ Imported play-by-play for {count} games!")

        except ValueError:
            print(f"❌ Invalid date format: {date_str}. Use YYYY-MM-DD")
            sys.exit(1)
        except ScraperError as e:
            print(f"❌ Failed to scrape play-by-play: {e}")
            logger.error("Play-by-play scraping failed", error=str(e), exc_info=True)
            sys.exit(1)

    def scrape_lineups(self, date_str: Optional[str] = None) -> None:
        """Scrape daily lineups and injury status from RotoWire.

        Args:
            date_str: Date in YYYY-MM-DD format (defaults to today)
        """
        try:
            target_date = None
            if date_str:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                print(f"🏀 Scraping lineups for {target_date}...")
            else:
                print("🏀 Scraping today's lineups...")

            count = self.rotowire_scraper.import_daily_lineups(target_date)
            print(f"✅ Imported {count} lineup entries!")

        except ValueError:
            print(f"❌ Invalid date format: {date_str}. Use YYYY-MM-DD")
            sys.exit(1)
        except RotoWireScraperError as e:
            print(f"❌ Failed to scrape lineups: {e}")
            logger.error("Lineup scraping failed", error=str(e), exc_info=True)
            sys.exit(1)

    def calculate_statistics(self, season: str) -> None:
        """Calculate team statistics for a season.

        Args:
            season: NBA season year
        """
        print(f"🏀 Calculating statistics for {season} season...")
        try:
            count = self.stats_calculator.generate_team_statistics(season)
            print(f"✅ Generated {count} statistical records!")

            print("🏀 Calculating win/loss streaks...")
            streak_count = self.stats_calculator.calculate_streaks(season)
            print(f"✅ Updated {streak_count} streak records!")

        except Exception as e:
            print(f"❌ Failed to calculate statistics: {e}")
            logger.error("Statistics calculation failed", error=str(e), exc_info=True)
            sys.exit(1)

    def predict_game(self, home_team: str, away_team: str, date_str: str) -> None:
        """Predict outcome of a specific game.

        Args:
            home_team: Home team name
            away_team: Away team name
            date_str: Game date in YYYY-MM-DD format
        """
        try:
            game_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            print(f"\n🏀 Predicting: {home_team} vs {away_team} on {game_date}\n")

            predictor = ClaudePredictor()
            prediction = predictor.predict_game(home_team, away_team, game_date)

            self._print_prediction(prediction)

        except ValueError:
            print(f"❌ Invalid date format: {date_str}. Use YYYY-MM-DD")
            sys.exit(1)
        except PredictionError as e:
            print(f"❌ Prediction failed: {e}")
            logger.error("Prediction failed", error=str(e), exc_info=True)
            sys.exit(1)

    def predict_date(self, date_str: str) -> None:
        """Predict all games for a specific date.

        Args:
            date_str: Date in YYYY-MM-DD format
        """
        try:
            game_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            print(f"\n🏀 Predicting all games for {game_date}\n")

            predictor = ClaudePredictor()
            predictions = predictor.predict_games_for_date(game_date)

            if not predictions:
                print("❌ No games found for this date")
                return

            for i, pred in enumerate(predictions, 1):
                print(f"\n{'='*60}")
                print(f"Game {i} of {len(predictions)}")
                print(f"{'='*60}")
                self._print_prediction(pred)

        except ValueError:
            print(f"❌ Invalid date format: {date_str}. Use YYYY-MM-DD")
            sys.exit(1)
        except PredictionError as e:
            print(f"❌ Prediction failed: {e}")
            logger.error("Date prediction failed", error=str(e), exc_info=True)
            sys.exit(1)

    def analyze_accuracy(self, season: str) -> None:
        """Analyze prediction accuracy for a season.

        Args:
            season: NBA season year
        """
        print(f"\n🏀 Analyzing prediction accuracy for {season} season...")
        print("⚠️  This will make multiple API calls and may take a while\n")

        try:
            predictor = ClaudePredictor()
            metrics = predictor.analyze_prediction_accuracy(season)

            print("\n" + "="*60)
            print("ACCURACY ANALYSIS")
            print("="*60)
            print(f"Games Analyzed: {metrics['games_analyzed']}")
            print(f"Correct Predictions: {metrics['correct_predictions']}")
            print(f"Accuracy: {metrics['accuracy_percentage']}%")
            print(f"Average Confidence: {metrics['average_confidence']}%")
            print("="*60 + "\n")

        except PredictionError as e:
            print(f"❌ Analysis failed: {e}")
            logger.error("Accuracy analysis failed", error=str(e), exc_info=True)
            sys.exit(1)

    def _print_prediction(self, prediction: dict) -> None:
        """Print prediction results in a formatted way.

        Args:
            prediction: Prediction dictionary
        """
        print(f"🏆 Predicted Winner: {prediction['predicted_winner']}")
        print(f"📊 Confidence: {prediction['confidence']}%")
        print(f"📈 Predicted Score: {prediction['predicted_score']['home']} - "
              f"{prediction['predicted_score']['away']}")
        print(f"\n🔑 Key Factors:")
        for factor in prediction['key_factors']:
            print(f"   • {factor}")
        print(f"\n📝 Analysis:")
        print(f"   {prediction['analysis']}\n")


def main() -> None:
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="NBA Predictor - AI-powered NBA game prediction system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize database
  python -m nba_predictor.cli init

  # Scrape games for one month
  python -m nba_predictor.cli scrape-games 2024 january

  # Scrape games for multiple months
  python -m nba_predictor.cli scrape-games 2024 january february march

  # Scrape games and play-by-play data
  python -m nba_predictor.cli scrape-games 2024 january february --scrape-pbp

  # Scrape daily lineups and injury status (today)
  python -m nba_predictor.cli scrape-lineups

  # Scrape lineups for a specific date
  python -m nba_predictor.cli scrape-lineups 2024-01-15

  # Calculate statistics
  python -m nba_predictor.cli calculate-stats 2024

  # Predict a game
  python -m nba_predictor.cli predict "Los Angeles Lakers" "Boston Celtics" 2024-01-15

  # Predict all games for a date
  python -m nba_predictor.cli predict-date 2024-01-15

  # Analyze accuracy
  python -m nba_predictor.cli analyze-accuracy 2024
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Init command
    subparsers.add_parser("init", help="Initialize database")

    # Scrape games command
    scrape_parser = subparsers.add_parser("scrape-games", help="Scrape games for one or more months")
    scrape_parser.add_argument("season", help="NBA season year (e.g., 2024)")
    scrape_parser.add_argument(
        "months",
        nargs='+',
        help="Month name(s) (e.g., january, february, march). Can specify multiple months separated by spaces",
    )
    scrape_parser.add_argument(
        "--scrape-pbp",
        action="store_true",
        default=False,
        help="Also scrape play-by-play data for games in these months",
    )

    # Scrape play-by-play command
    pbp_parser = subparsers.add_parser("scrape-pbp", help="Scrape play-by-play data")
    pbp_parser.add_argument("date", help="Date in YYYY-MM-DD format")

    # Scrape lineups command
    lineups_parser = subparsers.add_parser(
        "scrape-lineups", help="Scrape daily lineups and injury status from RotoWire"
    )
    lineups_parser.add_argument(
        "date",
        nargs="?",
        help="Date in YYYY-MM-DD format (optional, defaults to today)",
    )

    # Calculate stats command
    stats_parser = subparsers.add_parser("calculate-stats", help="Calculate team statistics")
    stats_parser.add_argument("season", help="NBA season year (e.g., 2024)")

    # Predict game command
    predict_parser = subparsers.add_parser("predict", help="Predict a specific game")
    predict_parser.add_argument("home_team", help="Home team name")
    predict_parser.add_argument("away_team", help="Away team name")
    predict_parser.add_argument("date", help="Game date in YYYY-MM-DD format")

    # Predict date command
    predict_date_parser = subparsers.add_parser(
        "predict-date", help="Predict all games for a date"
    )
    predict_date_parser.add_argument("date", help="Date in YYYY-MM-DD format")

    # Analyze accuracy command
    accuracy_parser = subparsers.add_parser("analyze-accuracy", help="Analyze prediction accuracy")
    accuracy_parser.add_argument("season", help="NBA season year (e.g., 2024)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cli = NBA_Predictor_CLI()

    if args.command == "init":
        cli.init_database()
    elif args.command == "scrape-games":
        cli.scrape_games(args.season, args.months, args.scrape_pbp)
    elif args.command == "scrape-pbp":
        cli.scrape_play_by_play(args.date)
    elif args.command == "scrape-lineups":
        cli.scrape_lineups(args.date)
    elif args.command == "calculate-stats":
        cli.calculate_statistics(args.season)
    elif args.command == "predict":
        cli.predict_game(args.home_team, args.away_team, args.date)
    elif args.command == "predict-date":
        cli.predict_date(args.date)
    elif args.command == "analyze-accuracy":
        cli.analyze_accuracy(args.season)


if __name__ == "__main__":
    main()
