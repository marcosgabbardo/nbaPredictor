"""Game-related database models."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from nba_predictor.models.database import Base


class Game(Base):
    """NBA game model."""

    __tablename__ = "nba_game"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    season: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    id2: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    overtime: Mapped[Optional[str]] = mapped_column(String(2))

    # Teams
    home_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    away_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Scores
    home_point: Mapped[Optional[int]] = mapped_column(Integer)
    away_point: Mapped[Optional[int]] = mapped_column(Integer)

    # Quarter scores
    home_p1: Mapped[Optional[int]] = mapped_column(Integer)
    home_p2: Mapped[Optional[int]] = mapped_column(Integer)
    home_p3: Mapped[Optional[int]] = mapped_column(Integer)
    home_p4: Mapped[Optional[int]] = mapped_column(Integer)

    away_p1: Mapped[Optional[int]] = mapped_column(Integer)
    away_p2: Mapped[Optional[int]] = mapped_column(Integer)
    away_p3: Mapped[Optional[int]] = mapped_column(Integer)
    away_p4: Mapped[Optional[int]] = mapped_column(Integer)

    # Advanced stats - Home
    home_pace: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 3))
    home_efg: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 3))
    home_tov: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 3))
    home_orb: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 3))
    home_ftfga: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 3))
    home_ortg: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 3))

    # Advanced stats - Away
    away_pace: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 3))
    away_efg: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 3))
    away_tov: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 3))
    away_orb: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 3))
    away_ftfga: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 3))
    away_ortg: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 3))

    def __repr__(self) -> str:
        return (
            f"<Game(date='{self.date}', "
            f"home='{self.home_name}', away='{self.away_name}', "
            f"score={self.home_point}-{self.away_point})>"
        )


class PlayByPlay(Base):
    """Play-by-play game data model."""

    __tablename__ = "nba_playbyplay"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    quarter: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    duration: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, index=True)

    home_comment: Mapped[Optional[str]] = mapped_column(Text)
    home_score: Mapped[Optional[int]] = mapped_column(Integer)

    away_comment: Mapped[Optional[str]] = mapped_column(Text)
    away_score: Mapped[Optional[int]] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"<PlayByPlay(game='{self.game_id}', quarter={self.quarter}, duration={self.duration})>"


class PlayerGameStats(Base):
    """Player game statistics model."""

    __tablename__ = "nba_player_game_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    game_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    season: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    team_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    player_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    is_starter: Mapped[bool] = mapped_column(Boolean, default=False)

    # Playing time
    minutes_played: Mapped[Optional[str]] = mapped_column(String(10))

    # Shooting stats
    field_goals: Mapped[int] = mapped_column(Integer, default=0)
    field_goal_attempts: Mapped[int] = mapped_column(Integer, default=0)
    field_goal_percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 3))

    # Three-point stats
    three_pointers: Mapped[int] = mapped_column(Integer, default=0)
    three_point_attempts: Mapped[int] = mapped_column(Integer, default=0)
    three_point_percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 3))

    # Free throw stats
    free_throws: Mapped[int] = mapped_column(Integer, default=0)
    free_throw_attempts: Mapped[int] = mapped_column(Integer, default=0)
    free_throw_percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 3))

    # Rebounds
    offensive_rebounds: Mapped[int] = mapped_column(Integer, default=0)
    defensive_rebounds: Mapped[int] = mapped_column(Integer, default=0)
    total_rebounds: Mapped[int] = mapped_column(Integer, default=0)

    # Other stats
    assists: Mapped[int] = mapped_column(Integer, default=0)
    steals: Mapped[int] = mapped_column(Integer, default=0)
    blocks: Mapped[int] = mapped_column(Integer, default=0)
    turnovers: Mapped[int] = mapped_column(Integer, default=0)
    personal_fouls: Mapped[int] = mapped_column(Integer, default=0)
    points: Mapped[int] = mapped_column(Integer, default=0)

    # Plus/minus
    plus_minus: Mapped[Optional[str]] = mapped_column(String(10))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    def __repr__(self) -> str:
        return (
            f"<PlayerGameStats(game='{self.game_id}', "
            f"player='{self.player_name}', team='{self.team_name}', "
            f"pts={self.points})>"
        )
