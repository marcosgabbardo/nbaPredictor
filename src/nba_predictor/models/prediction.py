"""Prediction-related database models."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, DateTime, Integer, Numeric, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nba_predictor.models.database import Base


class Prediction(Base):
    """AI prediction model for NBA games."""

    __tablename__ = "nba_prediction"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Game reference
    game_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    game_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    season: Mapped[Optional[str]] = mapped_column(String(10), index=True)

    # Teams
    home_team: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    away_team: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Prediction details
    predicted_winner: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    predicted_home_score: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_away_score: Mapped[int] = mapped_column(Integer, nullable=False)

    # Analysis
    analysis: Mapped[str] = mapped_column(Text, nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )
    model_version: Mapped[Optional[str]] = mapped_column(String(50))

    # Actual results (to be filled after the game)
    actual_winner: Mapped[Optional[str]] = mapped_column(String(50))
    actual_home_score: Mapped[Optional[int]] = mapped_column(Integer)
    actual_away_score: Mapped[Optional[int]] = mapped_column(Integer)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean)

    # Relationship to factors
    factors: Mapped[list["PredictionFactor"]] = relationship(
        "PredictionFactor", back_populates="prediction", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Prediction(date='{self.game_date}', "
            f"home='{self.home_team}', away='{self.away_team}', "
            f"winner='{self.predicted_winner}', confidence={self.confidence})>"
        )


class PredictionFactor(Base):
    """Key factors for AI predictions."""

    __tablename__ = "nba_prediction_factor"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prediction_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("nba_prediction.id"), nullable=False, index=True
    )
    factor: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationship to prediction
    prediction: Mapped["Prediction"] = relationship("Prediction", back_populates="factors")

    def __repr__(self) -> str:
        return f"<PredictionFactor(prediction_id={self.prediction_id}, factor='{self.factor}')>"
