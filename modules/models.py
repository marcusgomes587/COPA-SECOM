import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, ForeignKey, DateTime, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from modules.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    total_score = Column(Integer, default=0, nullable=False)

    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    special_bet = relationship("SpecialBet", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Match(Base):
    __tablename__ = "matches"

    match_id = Column(Integer, primary_key=True)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    kickoff_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="SCHEDULED", nullable=False)
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)

    predictions = relationship("Prediction", back_populates="match", cascade="all, delete-orphan")


class Prediction(Base):
    __tablename__ = "predictions"
    __table_args__ = (
        UniqueConstraint("user_id", "match_id", name="uq_user_match"),
    )

    prediction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.match_id", ondelete="CASCADE"), nullable=False)
    predicted_home_score = Column(Integer, nullable=False)
    predicted_away_score = Column(Integer, nullable=False)
    points_earned = Column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="predictions")
    match = relationship("Match", back_populates="predictions")


class SpecialBet(Base):
    __tablename__ = "special_bets"

    bet_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    champion_team = Column(String, nullable=True)
    top_scorer = Column(String, nullable=True)
    best_player = Column(String, nullable=True)

    user = relationship("User", back_populates="special_bet")
