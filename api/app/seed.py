import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Gender, User

SEED_USERS: list[tuple[str, Gender]] = [
    ("Münevver", Gender.F),
    ("Hüseyin", Gender.M),
    ("Murat", Gender.M),
    ("Melih", Gender.M),
    ("Büşra", Gender.F),
    ("Yılmaz can", Gender.M),
    ("Mert", Gender.M),
    ("Ceren", Gender.F),
    ("Erdem", Gender.M),
    ("Evrim", Gender.F),
    ("Burak Kaan", Gender.M),
    ("Nilhan", Gender.F),
    ("Arif", Gender.M),
    ("Görkem", Gender.M),
    ("Mehmet Akif", Gender.M),
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
