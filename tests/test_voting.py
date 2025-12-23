from .helpers import auth_headers, create_event, create_users, login_user, set_participants


def test_voting_rejects_self_vote(client):
    admin = login_user(client, "Münevver", "F")
    users = create_users(
        client,
        [("player1", "M"), ("player2", "F"), ("player3", "M")],
    )
    event_id = create_event(client, admin["access_token"])
    set_participants(
        client,
        admin["access_token"],
        event_id,
        [users["player1"]["user_id"], users["player2"]["user_id"], users["player3"]["user_id"]],
    )
    token = users["player1"]["access_token"]

    response = client.post(
        f"/api/events/{event_id}/votes",
        json={"target_user_id": users["player1"]["user_id"], "score": 8},
        headers=auth_headers(token),
    )
    assert response.status_code == 400


def test_voting_allows_other_users(client):
    admin = login_user(client, "Münevver", "F")
    users = create_users(
        client,
        [("voter1", "M"), ("voter2", "F"), ("voter3", "M")],
    )
    event_id = create_event(client, admin["access_token"])
    set_participants(
        client,
        admin["access_token"],
        event_id,
        [users["voter1"]["user_id"], users["voter2"]["user_id"], users["voter3"]["user_id"]],
    )
    token = users["voter1"]["access_token"]

    for target in (users["voter2"], users["voter3"]):
        response = client.post(
            f"/api/events/{event_id}/votes",
            json={"target_user_id": target["user_id"], "score": 7},
            headers=auth_headers(token),
        )
        assert response.status_code == 201

    duplicate = client.post(
        f"/api/events/{event_id}/votes",
        json={"target_user_id": users["voter2"]["user_id"], "score": 7},
        headers=auth_headers(token),
    )
    assert duplicate.status_code == 409
