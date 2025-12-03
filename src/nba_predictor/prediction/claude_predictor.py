"""Claude AI-powered NBA game predictor."""

import json
from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional

from anthropic import Anthropic

from nba_predictor.core.config import get_settings
from nba_predictor.core.logger import get_logger
from nba_predictor.models import Game, TeamHistory, get_db

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
        self, home_team: str, away_team: str, game_date: date
    ) -> Dict[str, Any]:
        """Predict outcome of a specific game.

        Args:
            home_team: Home team name
            away_team: Away team name
            game_date: Date of the game

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

            # Prepare context for Claude
            context = self._prepare_prediction_context(
                home_team, away_team, home_stats, away_stats
            )

            # Get prediction from Claude
            prediction = self._get_claude_prediction(context)

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
                    "last_3": float(history.pointavg3a) if history.pointavg3a else 0.0,
                    "last_5": float(history.pointavg5a) if history.pointavg5a else 0.0,
                    "last_10": float(history.pointavg10a) if history.pointavg10a else 0.0,
                    "overall": float(history.pointavga) if history.pointavga else 0.0,
                },
                "advanced_metrics": {
                    "pace": float(history.pace_avg1) if history.pace_avg1 else 0.0,
                    "efg_percentage": float(history.efg_avg1) if history.efg_avg1 else 0.0,
                    "turnover_percentage": (
                        float(history.tov_avg1) if history.tov_avg1 else 0.0
                    ),
                    "offensive_rebound_percentage": (
                        float(history.orb_avg1) if history.orb_avg1 else 0.0
                    ),
                    "free_throw_rate": (
                        float(history.ftfga_avg1) if history.ftfga_avg1 else 0.0
                    ),
                    "offensive_rating": (
                        float(history.ortg_avg1) if history.ortg_avg1 else 0.0
                    ),
                },
                "days_since_last_game": history.day_diff,
            }

            return stats

    def _prepare_prediction_context(
        self,
        home_team: str,
        away_team: str,
        home_stats: Dict[str, Any],
        away_stats: Dict[str, Any],
    ) -> str:
        """Prepare context for Claude prediction.

        Args:
            home_team: Home team name
            away_team: Away team name
            home_stats: Home team statistics
            away_stats: Away team statistics

        Returns:
            Formatted context string
        """
        context = f"""You are an expert NBA analyst. Analyze the following matchup and provide a prediction.

MATCHUP: {home_team} (Home) vs {away_team} (Away)

HOME TEAM STATISTICS ({home_team}):
{json.dumps(home_stats, indent=2)}

AWAY TEAM STATISTICS ({away_team}):
{json.dumps(away_stats, indent=2)}

Please analyze this matchup considering:
1. Recent form and momentum (win streaks, recent performance)
2. Offensive and defensive efficiency (points scored vs allowed)
3. Advanced metrics (pace, eFG%, turnover rate, offensive rating)
4. Rest factors (days since last game)
5. Home court advantage

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
                        game.home_name, game.away_name, game.date
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
