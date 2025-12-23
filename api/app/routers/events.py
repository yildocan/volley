import os
from datetime import date, datetime

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..deps import get_current_user, get_db
from ..models import Event, EventParticipant, User, Vote
from ..schemas import (
    EventCreate,
    EventOut,
    ParticipantsUpdate,
    ScoreOut,
    TeamResponse,
    UserOut,
    VoteCreate,
)
from ..teams import PlayerScore, generate_balanced_teams
from ..utils import is_admin_user


router = APIRouter(prefix="/api/events", tags=["events"])

DEFAULT_EVENT_DATE = date(2025, 12, 25)


@router.get("", response_model=list[EventOut])
def list_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if is_admin_user(current_user):
        events = db.scalars(select(Event).order_by(Event.date)).all()
    else:
        events = db.scalars(
            select(Event)
            .join(EventParticipant, EventParticipant.event_id == Event.id)
            .where(EventParticipant.user_id == current_user.id)
            .order_by(Event.date)
        ).all()
    if not events and is_admin_user(current_user):
        event = Event(date=DEFAULT_EVENT_DATE, weekly_recurrence=True)
        db.add(event)
        db.commit()
        db.refresh(event)
        events = [event]
    return events


def _parse_date(value: str | date | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    candidate = value.strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(candidate, fmt).date()
        except ValueError:
            continue
    try:
        return date.fromisoformat(candidate)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid date format") from exc


def _ensure_thursday(payload_date: date) -> None:
    if payload_date.weekday() != 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voting is only allowed for Thursday events",
        )


@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreate | None = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not is_admin_user(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    payload_date = _parse_date(payload.date) if payload else None
    if payload is None or payload_date is None:
        existing = db.scalar(select(Event).where(Event.date == DEFAULT_EVENT_DATE))
        if existing:
            return existing
        event = Event(date=DEFAULT_EVENT_DATE, weekly_recurrence=True)
    else:
        _ensure_thursday(payload_date)
        existing = db.scalar(select(Event).where(Event.date == payload_date))
        if existing:
            return existing
        event = Event(date=payload_date, weekly_recurrence=payload.weekly_recurrence)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/{event_id}", response_model=EventOut)
def get_event(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if not is_admin_user(current_user):
        participant_ids = _participant_ids(db, event_id, require=False)
        if current_user.id not in participant_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return event


@router.post("/{event_id}/votes", status_code=status.HTTP_201_CREATED)
def create_vote(
    event_id: str,
    payload: VoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if event.date.weekday() != 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Voting is only allowed on Thursdays")
    participant_ids = _participant_ids(db, event_id)
    if current_user.id not in participant_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not in this event")
    if payload.target_user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot vote for yourself")
    if payload.target_user_id not in participant_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Target user is not in this event")
    target = db.get(User, payload.target_user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found")
    vote = Vote(
        event_id=event_id,
        voter_id=current_user.id,
        target_user_id=payload.target_user_id,
        score=payload.score,
    )
    db.add(vote)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Vote already exists")
    return {"status": "ok"}


def _min_required_voters() -> int:
    value = os.getenv("MIN_VOTERS_FOR_RESULTS", "12")
    try:
        return max(2, int(value))
    except ValueError:
        return 12


def _participant_ids(db: Session, event_id: str, require: bool = True) -> list[str]:
    participant_ids = db.scalars(
        select(EventParticipant.user_id).where(EventParticipant.event_id == event_id)
    ).all()
    if require and not participant_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Participants not configured")
    return participant_ids


def _completed_voter_ids(db: Session, event_id: str) -> list[str]:
    participant_ids = _participant_ids(db, event_id)
    participant_count = len(participant_ids)
    if participant_count < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough participants")
    rows = db.execute(
        select(Vote.voter_id, func.count().label("vote_count"))
        .where(Vote.event_id == event_id)
        .where(Vote.voter_id.in_(participant_ids))
        .group_by(Vote.voter_id)
    ).all()
    return [row.voter_id for row in rows if row.vote_count == participant_count - 1]


def _ensure_min_completed(db: Session, event_id: str) -> list[str]:
    completed = _completed_voter_ids(db, event_id)
    min_required = _min_required_voters()
    if len(completed) < min_required:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Completed voters: {len(completed)}/{min_required}. At least {min_required} completed voters required before computing teams",
        )
    return completed


@router.get("/{event_id}/progress")
def get_progress(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if not is_admin_user(current_user):
        participant_ids = _participant_ids(db, event_id, require=False)
        if current_user.id not in participant_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    completed = _completed_voter_ids(db, event_id)
    min_required = _min_required_voters()
    return {
        "completed_voters": len(completed),
        "required_voters": min_required,
        "can_show_results": len(completed) >= min_required,
    }


@router.get("/{event_id}/participants", response_model=list[UserOut])
def get_participants(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    participant_ids = _participant_ids(db, event_id, require=False)
    if not is_admin_user(current_user) and current_user.id not in participant_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return db.scalars(select(User).where(User.id.in_(participant_ids)).order_by(User.username)).all()


@router.put("/{event_id}/participants", response_model=list[UserOut])
def set_participants(
    event_id: str,
    payload: ParticipantsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not is_admin_user(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if event.date.weekday() != 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Voting is only allowed on Thursdays")
    unique_ids = list(dict.fromkeys(payload.user_ids))
    users = db.scalars(select(User).where(User.id.in_(unique_ids))).all()
    if len(users) != len(unique_ids):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more users not found")

    db.execute(delete(EventParticipant).where(EventParticipant.event_id == event_id))
    db.add_all([EventParticipant(event_id=event_id, user_id=user.id) for user in users])
    db.commit()
    return users


@router.get("/{event_id}/scores", response_model=list[ScoreOut])
def get_scores(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if not is_admin_user(current_user):
        participant_ids = _participant_ids(db, event_id, require=False)
        if current_user.id not in participant_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    completed = _ensure_min_completed(db, event_id)

    rows = db.execute(
        select(
            User.id,
            User.username,
            User.gender,
            func.avg(Vote.score).label("avg_score"),
        )
        .join(Vote, Vote.target_user_id == User.id)
        .where(Vote.event_id == event_id)
        .where(User.id.in_(completed))
        .where(Vote.voter_id.in_(completed))
        .where(Vote.target_user_id.in_(completed))
        .group_by(User.id)
        .order_by(User.username)
    ).all()

    return [
        ScoreOut(
            user_id=row.id,
            username=row.username,
            gender=row.gender,
            average_score=round(float(row.avg_score), 2),
        )
        for row in rows
    ]


@router.get("/{event_id}/teams", response_model=TeamResponse)
def get_teams(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if not is_admin_user(current_user):
        participant_ids = _participant_ids(db, event_id, require=False)
        if current_user.id not in participant_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    completed = _ensure_min_completed(db, event_id)

    if len(completed) % 2 != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Completed voter count must be even to split teams evenly",
        )

    rows = db.execute(
        select(
            User.id,
            User.username,
            User.gender,
            func.avg(Vote.score).label("avg_score"),
        )
        .join(Vote, Vote.target_user_id == User.id)
        .where(Vote.event_id == event_id)
        .where(User.id.in_(completed))
        .where(Vote.voter_id.in_(completed))
        .where(Vote.target_user_id.in_(completed))
        .group_by(User.id)
    ).all()

    players = [
        PlayerScore(
            user_id=row.id,
            username=row.username,
            gender=row.gender,
            average_score=float(row.avg_score),
        )
        for row in rows
    ]

    try:
        result = generate_balanced_teams(players)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    def build_stats(team: list[PlayerScore]) -> dict:
        total = sum(p.average_score for p in team)
        avg = total / len(team) if team else 0
        gender_counts = {"M": 0, "F": 0}
        for player in team:
            gender_counts[player.gender] += 1
        return {
            "total_score": round(total, 2),
            "average_score": round(avg, 2),
            "gender_counts": gender_counts,
        }

    def to_score_out(player: PlayerScore) -> ScoreOut:
        return ScoreOut(
            user_id=player.user_id,
            username=player.username,
            gender=player.gender,
            average_score=round(player.average_score, 2),
        )

    team_a = [to_score_out(player) for player in result.team_a]
    team_b = [to_score_out(player) for player in result.team_b]

    return TeamResponse(
        team_a=team_a,
        team_b=team_b,
        summary={
            "team_a": build_stats(result.team_a),
            "team_b": build_stats(result.team_b),
        },
    )
