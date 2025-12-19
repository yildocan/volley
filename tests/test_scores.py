from .helpers import auth_headers, create_users, get_event_id


def test_average_scores(client):
    tokens, users = create_users(
        client,
        [("alpha", "M"), ("bravo", "F"), ("charlie", "M")],
    )
    event_id = get_event_id(client)

    id_map = {user["username"]: user["id"] for user in users}

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
                headers=auth_headers(tokens[voter]),
            )
            assert response.status_code == 201

    response = client.get(
        f"/api/events/{event_id}/scores",
        headers=auth_headers(tokens["alpha"]),
    )
    assert response.status_code == 200
    data = {item["username"]: item["average_score"] for item in response.json()}

    assert data["alpha"] == 4.5
    assert data["bravo"] == 6.5
    assert data["charlie"] == 9.0
