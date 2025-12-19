import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Gender, User

SEED_USERS: list[tuple[str, Gender]] = [
    ("Münevver", Gender.F),
    ("Abdullah", Gender.M),
    ("Arif", Gender.M),
    ("Begüm", Gender.F),
    ("Doğa", Gender.F),
    ("Ecs", Gender.M),
    ("Erdem", Gender.M),
    ("evrim", Gender.F),
    ("Görkem", Gender.M),
    ("Gülşah", Gender.F),
    ("hüseyin", Gender.M),
    ("kaan", Gender.M),
    ("Mcs", Gender.M),
    ("Mehmet Akif", Gender.M),
    ("Nilhan", Gender.F),
    ("Yılmaz Can", Gender.M),
    ("Ömür", Gender.F),
]


def seed_users(db: Session) -> None:
    if os.getenv("SEED_USERS", "true").lower() != "true":
        return
    existing = {user.username for user in db.scalars(select(User)).all()}
    new_users = [
        User(username=username, gender=gender)
        for username, gender in SEED_USERS
        if username not in existing
    ]
    if new_users:
        db.add_all(new_users)
        db.commit()
