from .helpers import auth_headers, create_event, create_users, login_user, set_participants


def test_average_scores(client):
    admin = login_user(client, "Münevver", "F")
    users = create_users(
        client,
        [("alpha", "M"), ("bravo", "F"), ("charlie", "M")],
    )
    event_id = create_event(client, admin["access_token"])
    set_participants(
        client,
        admin["access_token"],
        event_id,
        [users["alpha"]["user_id"], users["bravo"]["user_id"], users["charlie"]["user_id"]],
    )

    id_map = {name: data["user_id"] for name, data in users.items()}

    votes = {
        "alpha": {"bravo": 6, "charlie": 8},
        "bravo": {"alpha": 4, "charlie": 10},
        "charlie": {"alpha": 5, "bravo": 7},
    }

    for voter, targets in votes.items():
        for target, score in targets.items():
            response = client.post(
                f"/api/events/{event_id}/votes",
                json={"target_user_id": id_map[target], "score": score},
                headers=auth_headers(users[voter]["access_token"]),
            )
            assert response.status_code == 201

    response = client.get(
        f"/api/events/{event_id}/scores",
        headers=auth_headers(users["alpha"]["access_token"]),
    )
    assert response.status_code == 200
    data = {item["username"]: item["average_score"] for item in response.json()}

    assert data["alpha"] == 4.5
    assert data["bravo"] == 6.5
    assert data["charlie"] == 9.0
