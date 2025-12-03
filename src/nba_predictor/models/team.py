"""Team-related database models."""

from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from nba_predictor.models.database import Base


class Team(Base):
    """NBA team model."""

    __tablename__ = "nba_team"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    abbreviation: Mapped[str] = mapped_column(String(10), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False, default="NBA")

    def __repr__(self) -> str:
        return f"<Team(name='{self.name}', abbreviation='{self.abbreviation}')>"


class TeamHistory(Base):
    """Team historical statistics model."""

    __tablename__ = "nba_team_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    team_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    season: Mapped[str] = mapped_column(String(10), nullable=False)

    # Win statistics
    last1: Mapped[Optional[int]] = mapped_column(Integer)
    last3: Mapped[Optional[int]] = mapped_column(Integer)
    last5: Mapped[Optional[int]] = mapped_column(Integer)
    last10: Mapped[Optional[int]] = mapped_column(Integer)
    win: Mapped[Optional[int]] = mapped_column(Integer)
    game: Mapped[Optional[int]] = mapped_column(Integer)
    win_streak: Mapped[Optional[int]] = mapped_column(Integer)
    loss_streak: Mapped[Optional[int]] = mapped_column(Integer)

    # Point averages
    pointavg1: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    pointavg3: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    pointavg5: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    pointavg10: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    pointavg: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))

    # Point averages against
    pointavg1a: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    pointavg3a: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    pointavg5a: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    pointavg10a: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    pointavga: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))

    # Advanced metrics - Total averages
    pace_avg: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    efg_avg: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    tov_avg: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    orb_avg: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    ftfga_avg: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    ortg_avg: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))

    # Advanced metrics - Last 1 game
    pace_avg1: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    efg_avg1: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    tov_avg1: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    orb_avg1: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    ftfga_avg1: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    ortg_avg1: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))

    # Advanced metrics - Last 3 games
    pace_avg3: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    efg_avg3: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    tov_avg3: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    orb_avg3: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    ftfga_avg3: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    ortg_avg3: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))

    # Advanced metrics - Last 5 games
    pace_avg5: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    efg_avg5: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    tov_avg5: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    orb_avg5: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    ftfga_avg5: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    ortg_avg5: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))

    # Advanced metrics - Last 10 games
    pace_avg10: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    efg_avg10: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    tov_avg10: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    orb_avg10: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    ftfga_avg10: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    ortg_avg10: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))

    # Quarter averages
    p1_avg: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    p2_avg: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    p3_avg: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    p4_avg: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))

    p1_avg5: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    p2_avg5: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    p3_avg5: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    p4_avg5: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))

    p1_avg10: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    p2_avg10: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    p3_avg10: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    p4_avg10: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))

    # Other
    overtime: Mapped[Optional[str]] = mapped_column(String(3))
    day_diff: Mapped[Optional[int]] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"<TeamHistory(team='{self.team_name}', date='{self.date}')>"
