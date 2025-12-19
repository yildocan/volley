from .helpers import auth_headers, login_user


def test_login_creates_user(client):
    token = login_user(client, "alex", "M")
    assert isinstance(token, str)
    assert token
    response = client.get("/api/users", headers=auth_headers(token))
    assert response.status_code == 200
    assert any(user["username"] == "alex" for user in response.json())
