from __future__ import annotations

from datetime import date
from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Gender(str, Enum):
    M = "M"
    F = "F"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    gender: Mapped[Gender] = mapped_column(String(1), nullable=False)

    votes_cast: Mapped[list[Vote]] = relationship(
        "Vote",
        back_populates="voter",
        foreign_keys="Vote.voter_id",
        cascade="all, delete-orphan",
    )
    votes_received: Mapped[list[Vote]] = relationship(
        "Vote",
        back_populates="target_user",
        foreign_keys="Vote.target_user_id",
        cascade="all, delete-orphan",
    )


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    date: Mapped[date] = mapped_column(Date, nullable=False)
    weekly_recurrence: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    votes: Mapped[list[Vote]] = relationship("Vote", back_populates="event", cascade="all, delete-orphan")


class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (
        UniqueConstraint("event_id", "voter_id", "target_user_id", name="uq_vote"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    event_id: Mapped[str] = mapped_column(String(36), ForeignKey("events.id"), nullable=False, index=True)
    voter_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    target_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)

    event: Mapped[Event] = relationship("Event", back_populates="votes")
    voter: Mapped[User] = relationship("User", back_populates="votes_cast", foreign_keys=[voter_id])
    target_user: Mapped[User] = relationship("User", back_populates="votes_received", foreign_keys=[target_user_id])
