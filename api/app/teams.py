from dataclasses import dataclass

from .models import Gender


@dataclass
class PlayerScore:
    user_id: str
    username: str
    gender: Gender
    average_score: float


@dataclass
class TeamResult:
    team_a: list[PlayerScore]
    team_b: list[PlayerScore]


def _team_stats(team: list[PlayerScore]) -> dict:
    total = sum(p.average_score for p in team)
    gender_counts = {"M": 0, "F": 0}
    for player in team:
        gender_counts[player.gender] += 1
    avg = total / len(team) if team else 0
    return {"total": total, "avg": avg, "gender_counts": gender_counts}


def _objective(team_a: list[PlayerScore], team_b: list[PlayerScore]) -> float:
    stats_a = _team_stats(team_a)
    stats_b = _team_stats(team_b)
    score_diff = abs(stats_a["total"] - stats_b["total"])
    gender_diff = abs(stats_a["gender_counts"]["M"] - stats_b["gender_counts"]["M"])
    size_diff = abs(len(team_a) - len(team_b))
    return score_diff + (gender_diff * 2) + (size_diff * 0.5)


def generate_balanced_teams(players: list[PlayerScore]) -> TeamResult:
    if len(players) < 12 or len(players) % 2 != 0:
        raise ValueError("Team generation requires an even number of players (min 12).")

    players_sorted = sorted(players, key=lambda p: p.average_score, reverse=True)
    team_a: list[PlayerScore] = []
    team_b: list[PlayerScore] = []
    team_size = len(players) // 2

    total_m = sum(1 for p in players_sorted if p.gender == Gender.M)
    total_f = sum(1 for p in players_sorted if p.gender == Gender.F)
    target_a_m = total_m // 2
    target_b_m = total_m - target_a_m
    target_a_f = total_f // 2
    target_b_f = total_f - target_a_f

    for player in players_sorted:
        if len(team_a) >= team_size:
            team_b.append(player)
            continue
        if len(team_b) >= team_size:
            team_a.append(player)
            continue

        gender = player.gender
        team_a_gender = {"M": sum(1 for p in team_a if p.gender == Gender.M),
                         "F": sum(1 for p in team_a if p.gender == Gender.F)}
        team_b_gender = {"M": sum(1 for p in team_b if p.gender == Gender.M),
                         "F": sum(1 for p in team_b if p.gender == Gender.F)}

        if gender == Gender.M:
            if team_a_gender["M"] >= target_a_m and team_b_gender["M"] < target_b_m:
                team_b.append(player)
                continue
            if team_b_gender["M"] >= target_b_m and team_a_gender["M"] < target_a_m:
                team_a.append(player)
                continue
        else:
            if team_a_gender["F"] >= target_a_f and team_b_gender["F"] < target_b_f:
                team_b.append(player)
                continue
            if team_b_gender["F"] >= target_b_f and team_a_gender["F"] < target_a_f:
                team_a.append(player)
                continue

        candidate_a = team_a + [player]
        candidate_b = team_b + [player]
        score_a = _objective(candidate_a, team_b)
        score_b = _objective(team_a, candidate_b)

        if score_a < score_b:
            team_a.append(player)
        elif score_b < score_a:
            team_b.append(player)
        else:
            if len(team_a) <= len(team_b):
                team_a.append(player)
            else:
                team_b.append(player)

    _swap_optimization(team_a, team_b)
    return TeamResult(team_a=team_a, team_b=team_b)


def _swap_optimization(team_a: list[PlayerScore], team_b: list[PlayerScore]) -> None:
    improved = True
    passes = 0
    while improved and passes < 2:
        improved = False
        passes += 1
        current_score = _objective(team_a, team_b)
        for i, player_a in enumerate(team_a):
            for j, player_b in enumerate(team_b):
                swapped_a = team_a[:]
                swapped_b = team_b[:]
                swapped_a[i], swapped_b[j] = player_b, player_a
                new_score = _objective(swapped_a, swapped_b)
                if new_score + 0.01 < current_score:
                    team_a[i], team_b[j] = player_b, player_a
                    current_score = new_score
                    improved = True
