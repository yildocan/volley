from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from .models import Gender


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    gender: Gender | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str


class UserOut(BaseModel):
    id: str
    username: str
    gender: Gender


class EventCreate(BaseModel):
    date: Optional[str] = None
    weekly_recurrence: bool = True


class EventOut(BaseModel):
    id: str
    date: date
    weekly_recurrence: bool


class VoteCreate(BaseModel):
    target_user_id: str
    score: int = Field(ge=1, le=10)


class ScoreOut(BaseModel):
    user_id: str
    username: str
    gender: Gender
    average_score: float


class TeamStats(BaseModel):
    total_score: float
    average_score: float
    gender_counts: dict[str, int]


class TeamResponse(BaseModel):
    team_a: list[ScoreOut]
    team_b: list[ScoreOut]
    summary: dict[str, TeamStats]
