from .helpers import auth_headers, create_users, get_event_id


def test_voting_rejects_self_vote(client):
    tokens, users = create_users(
        client,
        [("player1", "M"), ("player2", "F"), ("player3", "M")],
    )
    event_id = get_event_id(client)
    token = tokens["player1"]

    response = client.post(
        f"/api/events/{event_id}/votes",
        json={"target_user_id": users[0]["id"], "score": 8},
        headers=auth_headers(token),
    )
    assert response.status_code == 400


def test_voting_allows_other_users(client):
    tokens, users = create_users(
        client,
        [("voter1", "M"), ("voter2", "F"), ("voter3", "M")],
    )
    event_id = get_event_id(client)
    token = tokens["voter1"]

    for target in users[1:]:
        response = client.post(
            f"/api/events/{event_id}/votes",
            json={"target_user_id": target["id"], "score": 7},
            headers=auth_headers(token),
        )
        assert response.status_code == 201

    duplicate = client.post(
        f"/api/events/{event_id}/votes",
        json={"target_user_id": users[1]["id"], "score": 7},
        headers=auth_headers(token),
    )
    assert duplicate.status_code == 409
