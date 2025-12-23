from .helpers import login_user


def test_login_creates_user(client):
    data = login_user(client, "alex", "M")
    assert data["access_token"]
    assert data["user_id"]
    assert data["username"] == "alex"


def test_admin_detection(client):
    data = login_user(client, "Münevver", "F")
    assert data["is_admin"] is True
