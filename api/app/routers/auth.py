import os

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.security import create_access_token
from ..deps import get_db
from ..models import User
from ..schemas import LoginRequest, TokenResponse
from ..utils import is_admin_user, normalize_name


router = APIRouter(prefix="/api/auth", tags=["auth"])


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    prev_row = list(range(len(b) + 1))
    for i, char_a in enumerate(a, start=1):
        row = [i]
        for j, char_b in enumerate(b, start=1):
            insert_cost = row[j - 1] + 1
            delete_cost = prev_row[j] + 1
            replace_cost = prev_row[j - 1] + (char_a != char_b)
            row.append(min(insert_cost, delete_cost, replace_cost))
        prev_row = row
    return prev_row[-1]


def _find_best_match(users: list[User], username: str, max_distance: int = 2) -> User | None:
    target = normalize_name(username)
    best_user = None
    best_distance = None
    for user in users:
        candidate = normalize_name(user.username)
        distance = _levenshtein(target, candidate)
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_user = user
    if best_distance is not None and best_distance <= max_distance:
        return best_user
    return None

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    allow_self_register = os.getenv("ALLOW_SELF_REGISTER", "false").lower() == "true"

    if allow_self_register:
        user = db.scalar(select(User).where(User.username == payload.username))
        if user:
            token = create_access_token(user.id)
            return TokenResponse(
                access_token=token,
                user_id=user.id,
                username=user.username,
                is_admin=is_admin_user(user),
            )
        if payload.gender is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gender is required for first login",
            )
        user = User(username=payload.username, gender=payload.gender)
        db.add(user)
        db.commit()
        db.refresh(user)
        token = create_access_token(user.id)
        return TokenResponse(
            access_token=token,
            user_id=user.id,
            username=user.username,
            is_admin=is_admin_user(user),
        )

    users = db.scalars(select(User)).all()
    match = _find_best_match(users, payload.username)

    if match:
        token = create_access_token(match.id)
        return TokenResponse(
            access_token=token,
            user_id=match.id,
            username=match.username,
            is_admin=is_admin_user(match),
        )

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
