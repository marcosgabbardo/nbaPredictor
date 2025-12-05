"""Daily lineup database models."""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from nba_predictor.models.database import Base


class DailyLineup(Base):
    """Daily lineup and injury status model."""

    __tablename__ = "nba_daily_lineup"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scrape_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    game_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    team_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    player_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    position: Mapped[Optional[str]] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    injury_description: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    def __repr__(self) -> str:
        return (
            f"<DailyLineup(date='{self.game_date}', "
            f"team='{self.team_name}', player='{self.player_name}', "
            f"status='{self.status}')>"
        )
