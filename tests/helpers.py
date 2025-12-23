from typing import Iterable


def login_user(client, username: str, gender: str = "M") -> dict:
    response = client.post(
        "/api/auth/login",
        json={"username": username, "gender": gender},
    )
    assert response.status_code == 200, response.text
    return response.json()


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def create_event(client, admin_token: str, date: str = "2025-12-25") -> str:
    response = client.post(
        "/api/events",
        json={"date": date, "weekly_recurrence": False},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def set_participants(client, admin_token: str, event_id: str, user_ids: list[str]) -> None:
    response = client.put(
        f"/api/events/{event_id}/participants",
        json={"user_ids": user_ids},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200, response.text


def create_users(client, users: Iterable[tuple[str, str]]) -> dict[str, dict]:
    results = {}
    for username, gender in users:
        results[username] = login_user(client, username, gender)
    return results
