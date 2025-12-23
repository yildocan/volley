from .helpers import auth_headers, create_event, create_users, login_user, set_participants


def test_team_generation_balances_score_and_gender(client):
    users = [
        ("player01", "M"), ("player02", "M"), ("player03", "M"), ("player04", "M"), ("player05", "M"), ("player06", "M"),
        ("player07", "F"), ("player08", "F"), ("player09", "F"), ("player10", "F"), ("player11", "F"), ("player12", "F"),
    ]
    admin = login_user(client, "Münevver", "F")
    tokens = create_users(client, users)
    event_id = create_event(client, admin["access_token"])
    set_participants(
        client,
        admin["access_token"],
        event_id,
        [tokens[name]["user_id"] for name, _ in users],
    )
    id_map = {name: data["user_id"] for name, data in tokens.items()}

    target_scores = {
        "player01": 10,
        "player02": 9,
        "player03": 8,
        "player04": 7,
        "player05": 6,
        "player06": 5,
        "player07": 4,
        "player08": 3,
        "player09": 2,
        "player10": 1,
        "player11": 10,
        "player12": 9,
    }

    for voter_name, _ in users:
        for target_name, _ in users:
            if voter_name == target_name:
                continue
            response = client.post(
                f"/api/events/{event_id}/votes",
                json={"target_user_id": id_map[target_name], "score": target_scores[target_name]},
                headers=auth_headers(tokens[voter_name]["access_token"]),
            )
            assert response.status_code == 201

    response = client.get(
        f"/api/events/{event_id}/teams",
        headers=auth_headers(tokens["player01"]["access_token"]),
    )
    assert response.status_code == 200
    data = response.json()

    team_a = data["team_a"]
    team_b = data["team_b"]
    assert len(team_a) == 6
    assert len(team_b) == 6

    def gender_counts(team):
        counts = {"M": 0, "F": 0}
        for player in team:
            counts[player["gender"]] += 1
        return counts

    counts_a = gender_counts(team_a)
    counts_b = gender_counts(team_b)
    assert counts_a["M"] == 3
    assert counts_a["F"] == 3
    assert counts_b["M"] == 3
    assert counts_b["F"] == 3

    total_a = sum(player["average_score"] for player in team_a)
    total_b = sum(player["average_score"] for player in team_b)
    assert abs(total_a - total_b) <= 5
