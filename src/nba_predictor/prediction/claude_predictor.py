"""Claude AI-powered NBA game predictor."""

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from anthropic import Anthropic

from nba_predictor.core.config import get_settings
from nba_predictor.core.logger import get_logger
from nba_predictor.models import DailyLineup, Game, Prediction, PredictionFactor, TeamHistory, get_db

logger = get_logger(__name__)


class PredictionError(Exception):
    """Base exception for prediction errors."""

    pass


class ClaudePredictor:
    """AI-powered NBA game predictor using Claude."""

    def __init__(self) -> None:
        """Initialize Claude predictor."""
        self.settings = get_settings()

        if not self.settings.anthropic.api_key:
            raise PredictionError("Anthropic API key not configured")

        self.client = Anthropic(api_key=self.settings.anthropic.api_key)
        logger.info("Claude predictor initialized")

    def predict_game(
        self, home_team: str, away_team: str, game_date: date, save_to_db: bool = True
    ) -> Dict[str, Any]:
        """Predict outcome of a specific game.

        Args:
            home_team: Home team name
            away_team: Away team name
            game_date: Date of the game
            save_to_db: Whether to save prediction to database (default: True)

        Returns:
            Prediction dictionary with winner, confidence, and analysis

        Raises:
            PredictionError: If prediction fails
        """
        logger.info("Predicting game", home=home_team, away=away_team, date=game_date)

        try:
            # Gather team statistics
            home_stats = self._get_team_statistics(home_team, game_date)
            away_stats = self._get_team_statistics(away_team, game_date)

            if not home_stats or not away_stats:
                raise PredictionError("Insufficient data for prediction")

            # Gather lineup information
            home_lineup = self._get_lineup_info(home_team, game_date)
            away_lineup = self._get_lineup_info(away_team, game_date)

            # Prepare context for Claude
            context = self._prepare_prediction_context(
                home_team, away_team, home_stats, away_stats, home_lineup, away_lineup
            )

            # Get prediction from Claude
            prediction = self._get_claude_prediction(context)

            # Save to database if requested
            if save_to_db:
                prediction_id = self._save_prediction(
                    home_team=home_team,
                    away_team=away_team,
                    game_date=game_date,
                    prediction=prediction,
                )
                prediction["prediction_id"] = prediction_id

            logger.info(
                "Prediction complete",
                winner=prediction.get("predicted_winner"),
                confidence=prediction.get("confidence"),
            )

            return prediction

        except Exception as e:
            logger.error("Prediction failed", error=str(e), exc_info=True)
            raise PredictionError(f"Failed to predict game: {e}")

    def predict_games_for_date(self, game_date: date) -> List[Dict[str, Any]]:
        """Predict all games for a specific date.

        Args:
            game_date: Date to predict games for

        Returns:
            List of predictions
        """
        logger.info("Predicting games for date", date=game_date)

        with get_db() as db:
            games = db.query(Game).filter(Game.date == game_date).all()

            if not games:
                logger.warning("No games found for date", date=game_date)
                return []

            predictions = []

            for game in games:
                try:
                    prediction = self.predict_game(
                        game.home_name, game.away_name, game_date
                    )
                    prediction["game_id"] = game.id2
                    predictions.append(prediction)

                except PredictionError as e:
                    logger.error(
                        "Failed to predict game",
                        home=game.home_name,
                        away=game.away_name,
                        error=str(e),
                    )
                    continue

            logger.info("Date predictions complete", total=len(predictions))
            return predictions

    def _get_team_statistics(
        self, team_name: str, before_date: date
    ) -> Optional[Dict[str, Any]]:
        """Get team statistics before a specific date.

        Args:
            team_name: Team name
            before_date: Get stats before this date

        Returns:
            Dictionary of team statistics or None
        """
        with get_db() as db:
            history = (
                db.query(TeamHistory)
                .filter(TeamHistory.team_name == team_name, TeamHistory.date < before_date)
                .order_by(TeamHistory.date.desc())
                .first()
            )

            if not history:
                return None

            # Convert to dictionary with serializable values
            stats = {
                "team_name": history.team_name,
                "games_played": history.game,
                "wins": history.win,
                "win_percentage": (
                    float(history.win) / float(history.game)
                    if history.game and history.game > 0
                    else 0.0
                ),
                "recent_form": {
                    "last_1": history.last1,
                    "last_3": history.last3,
                    "last_5": history.last5,
                    "last_10": history.last10,
                },
                "win_streak": history.win_streak,
                "loss_streak": history.loss_streak,
                "point_averages": {
                    "last_1": float(history.pointavg1) if history.pointavg1 else 0.0,
                    "last_3": float(history.pointavg3) if history.pointavg3 else 0.0,
                    "last_5": float(history.pointavg5) if history.pointavg5 else 0.0,
                    "last_10": float(history.pointavg10) if history.pointavg10 else 0.0,
                    "overall": float(history.pointavg) if history.pointavg else 0.0,
                },
                "points_against_averages": {
                    "last_1": float(history.pointavg1a) if history.pointavg1a else 0.0,
                    "overall": float(history.pointavga) if history.pointavga else 0.0,
                },
                "advanced_metrics": {
                    "pace": float(history.pace_avg) if history.pace_avg else 0.0,
                    "efg_percentage": float(history.efg_avg) if history.efg_avg else 0.0,
                    "turnover_percentage": (
                        float(history.tov_avg) if history.tov_avg else 0.0
                    ),
                    "offensive_rebound_percentage": (
                        float(history.orb_avg) if history.orb_avg else 0.0
                    ),
                    "free_throw_rate": (
                        float(history.ftfga_avg) if history.ftfga_avg else 0.0
                    ),
                    "offensive_rating": (
                        float(history.ortg_avg) if history.ortg_avg else 0.0
                    ),
                },
                "days_since_last_game": history.day_diff,
            }

            return stats

    def _get_lineup_info(
        self, team_name: str, game_date: date
    ) -> Optional[Dict[str, Any]]:
        """Get lineup and injury information for a team on a specific date.

        Args:
            team_name: Team name
            game_date: Date of the game

        Returns:
            Dictionary with lineup information or None if no data available
        """
        with get_db() as db:
            # Get the most recent lineup data for this team and date
            # We look for data scraped on the same day or the day before
            lineups = (
                db.query(DailyLineup)
                .filter(
                    DailyLineup.team_name == team_name,
                    DailyLineup.game_date == game_date,
                )
                .all()
            )

            if not lineups:
                return None

            # Organize lineup data by status
            starters = []
            out = []
            questionable = []
            gtd = []
            other = []

            for lineup in lineups:
                player_info = {
                    "name": lineup.player_name,
                    "position": lineup.position,
                }

                if lineup.injury_description:
                    player_info["injury"] = lineup.injury_description

                if lineup.status == "Starter":
                    starters.append(player_info)
                elif lineup.status == "OUT":
                    out.append(player_info)
                elif lineup.status in ["Questionable", "Q"]:
                    questionable.append(player_info)
                elif lineup.status in ["GTD", "Game-Time Decision"]:
                    gtd.append(player_info)
                else:
                    other.append(player_info)

            lineup_info = {
                "has_data": True,
                "starters": starters,
                "injuries": {
                    "out": out,
                    "questionable": questionable,
                    "gtd": gtd,
                    "other": other,
                },
            }

            return lineup_info

    def _prepare_prediction_context(
        self,
        home_team: str,
        away_team: str,
        home_stats: Dict[str, Any],
        away_stats: Dict[str, Any],
        home_lineup: Optional[Dict[str, Any]] = None,
        away_lineup: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Prepare context for Claude prediction.

        Args:
            home_team: Home team name
            away_team: Away team name
            home_stats: Home team statistics
            away_stats: Away team statistics
            home_lineup: Home team lineup and injury info (optional)
            away_lineup: Away team lineup and injury info (optional)

        Returns:
            Formatted context string
        """
        context = f"""You are an expert NBA analyst. Analyze the following matchup and provide a prediction.

MATCHUP: {home_team} (Home) vs {away_team} (Away)

HOME TEAM STATISTICS ({home_team}):
{json.dumps(home_stats, indent=2)}

AWAY TEAM STATISTICS ({away_team}):
{json.dumps(away_stats, indent=2)}
"""

        # Add lineup information if available
        if home_lineup:
            context += f"""
HOME TEAM LINEUP & INJURY REPORT ({home_team}):
{json.dumps(home_lineup, indent=2)}
"""

        if away_lineup:
            context += f"""
AWAY TEAM LINEUP & INJURY REPORT ({away_team}):
{json.dumps(away_lineup, indent=2)}
"""

        lineup_analysis = ""
        if home_lineup or away_lineup:
            lineup_analysis = """
6. Player availability and lineup strength (consider impact of injuries, key players out, and starting lineup quality)"""

        context += f"""
Please analyze this matchup considering:
1. Recent form and momentum (win streaks, recent performance)
2. Offensive and defensive efficiency (points scored vs allowed)
3. Advanced metrics (pace, eFG%, turnover rate, offensive rating)
4. Rest factors (days since last game)
5. Home court advantage{lineup_analysis}

IMPORTANT: If lineup/injury data is provided, carefully consider:
- The impact of players listed as OUT on team performance
- The uncertainty of players listed as Questionable or GTD (Game-Time Decision)
- The quality and experience of the expected starting lineup
- How key injuries might affect team chemistry and rotations

Provide your prediction in the following JSON format:
{{
    "predicted_winner": "<team name>",
    "confidence": <0-100>,
    "predicted_score": {{"home": <score>, "away": <score>}},
    "key_factors": ["factor 1", "factor 2", "factor 3"],
    "analysis": "Detailed explanation of your prediction"
}}
"""
        return context

    def _get_claude_prediction(self, context: str) -> Dict[str, Any]:
        """Get prediction from Claude API.

        Args:
            context: Prediction context

        Returns:
            Parsed prediction dictionary

        Raises:
            PredictionError: If API call fails
        """
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2048,
                messages=[{"role": "user", "content": context}],
            )

            response_text = message.content[0].text

            # Extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                raise PredictionError("No JSON found in Claude response")

            json_str = response_text[json_start:json_end]
            prediction = json.loads(json_str)

            # Validate prediction structure
            required_fields = [
                "predicted_winner",
                "confidence",
                "predicted_score",
                "key_factors",
                "analysis",
            ]

            for field in required_fields:
                if field not in prediction:
                    raise PredictionError(f"Missing required field: {field}")

            return prediction

        except json.JSONDecodeError as e:
            logger.error("Failed to parse Claude response", error=str(e))
            raise PredictionError(f"Invalid JSON in Claude response: {e}")

        except Exception as e:
            logger.error("Claude API call failed", error=str(e))
            raise PredictionError(f"Claude API error: {e}")

    def _save_prediction(
        self,
        home_team: str,
        away_team: str,
        game_date: date,
        prediction: Dict[str, Any],
    ) -> int:
        """Save prediction to database.

        Args:
            home_team: Home team name
            away_team: Away team name
            game_date: Date of the game
            prediction: Prediction dictionary from Claude

        Returns:
            ID of the saved prediction

        Raises:
            PredictionError: If saving fails
        """
        try:
            with get_db() as db:
                # Get game_id and season if available
                game = (
                    db.query(Game)
                    .filter(
                        Game.date == game_date,
                        Game.home_name == home_team,
                        Game.away_name == away_team,
                    )
                    .first()
                )

                game_id = game.id2 if game else None
                season = game.season if game else None

                # Create prediction record
                prediction_record = Prediction(
                    game_id=game_id,
                    game_date=game_date,
                    season=season,
                    home_team=home_team,
                    away_team=away_team,
                    predicted_winner=prediction["predicted_winner"],
                    confidence=Decimal(str(prediction["confidence"])),
                    predicted_home_score=prediction["predicted_score"]["home"],
                    predicted_away_score=prediction["predicted_score"]["away"],
                    analysis=prediction["analysis"],
                    created_at=datetime.utcnow(),
                    model_version="claude-sonnet-4-5-20250929",
                )

                db.add(prediction_record)
                db.flush()  # Get the ID without committing

                # Create factor records
                for idx, factor in enumerate(prediction.get("key_factors", [])):
                    factor_record = PredictionFactor(
                        prediction_id=prediction_record.id,
                        factor=factor,
                        order=idx,
                    )
                    db.add(factor_record)

                # Check if game has results and update prediction accuracy
                if game and game.home_point is not None and game.away_point is not None:
                    actual_winner = (
                        home_team if game.home_point > game.away_point else away_team
                    )
                    prediction_record.actual_winner = actual_winner
                    prediction_record.actual_home_score = game.home_point
                    prediction_record.actual_away_score = game.away_point
                    prediction_record.is_correct = (
                        prediction["predicted_winner"] == actual_winner
                    )

                db.commit()

                logger.info(
                    "Prediction saved to database",
                    prediction_id=prediction_record.id,
                    home=home_team,
                    away=away_team,
                )

                return prediction_record.id

        except Exception as e:
            logger.error("Failed to save prediction", error=str(e), exc_info=True)
            raise PredictionError(f"Failed to save prediction: {e}")

    def analyze_prediction_accuracy(self, season: str) -> Dict[str, Any]:
        """Analyze prediction accuracy for a season.

        Args:
            season: NBA season year

        Returns:
            Accuracy metrics
        """
        logger.info("Analyzing prediction accuracy", season=season)

        with get_db() as db:
            games = (
                db.query(Game)
                .filter(Game.season == season, Game.home_point.isnot(None))
                .all()
            )

            total_games = len(games)
            correct_predictions = 0
            total_confidence = 0.0

            for game in games[:50]:  # Limit for cost reasons
                try:
                    prediction = self.predict_game(
                        game.home_name, game.away_name, game.date, save_to_db=False
                    )

                    # Determine actual winner
                    actual_winner = (
                        game.home_name
                        if game.home_point > game.away_point
                        else game.away_name
                    )

                    if prediction["predicted_winner"] == actual_winner:
                        correct_predictions += 1

                    total_confidence += prediction["confidence"]

                except Exception as e:
                    logger.warning("Skipped game in accuracy analysis", error=str(e))
                    continue

            accuracy = (
                correct_predictions / min(50, total_games) * 100
                if total_games > 0
                else 0.0
            )
            avg_confidence = total_confidence / min(50, total_games) if total_games > 0 else 0.0

            metrics = {
                "games_analyzed": min(50, total_games),
                "correct_predictions": correct_predictions,
                "accuracy_percentage": round(accuracy, 2),
                "average_confidence": round(avg_confidence, 2),
            }

            logger.info("Accuracy analysis complete", metrics=metrics)
            return metrics
