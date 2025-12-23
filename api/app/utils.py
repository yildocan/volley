import unicodedata

from .models import User


def normalize_name(value: str) -> str:
    value = value.strip().lower()
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char)).replace(" ", "")


def is_admin_user(user: User) -> bool:
    return normalize_name(user.username) == "munevver"
