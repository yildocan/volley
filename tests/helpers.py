from typing import Iterable


def login_user(client, username: str, gender: str = "M") -> str:
    response = client.post(
        "/api/auth/login",
        json={"username": username, "gender": gender},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def get_event_id(client) -> str:
    response = client.get("/api/events")
    assert response.status_code == 200, response.text
    return response.json()[0]["id"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def create_users(client, users: Iterable[tuple[str, str]]) -> tuple[dict, list[dict]]:
    tokens = {username: login_user(client, username, gender) for username, gender in users}
    token = next(iter(tokens.values()))
    response = client.get("/api/users", headers=auth_headers(token))
    assert response.status_code == 200, response.text
    return tokens, response.json()
