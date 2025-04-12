import requests
import pandas as pd
import time

API_KEY = "55f74033c9msh1ca200a87ce12c5p1c8d4ejsne2c385722ec4"
HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
}

SEASONS = [2021, 2022, 2023, 2024, 2025]
RATE_LIMIT_DELAY = 1.2

def get_teams():
    url = "https://api-nba-v1.p.rapidapi.com/teams"
    res = requests.get(url, headers=HEADERS)
    return {t["id"]: t["name"] for t in res.json()["response"] if t["nbaFranchise"]}

def get_games_by_season(season):
    games = []
    page = 1
    while True:
        url = f"https://api-nba-v1.p.rapidapi.com/games?season={season}&league=standard&page={page}"
        res = requests.get(url, headers=HEADERS)
        batch = res.json().get("response", [])
        if not batch:
            break
        games.extend(batch)
        page += 1
        time.sleep(RATE_LIMIT_DELAY)
    return games

def get_player_stats(game_id):
    url = f"https://api-nba-v1.p.rapidapi.com/players/statistics?game={game_id}"
    res = requests.get(url, headers=HEADERS)
    return res.json().get("response", [])

def main():
    all_games = []
    all_player_stats = []

    for season in SEASONS:
        print(f"📅 Season {season}")
        games = get_games_by_season(season)

        for game in games:
            game_id = game.get("id")
            if not game_id:
                continue
            player_stats = get_player_stats(game_id)
            if not player_stats:
                continue

            game_record = {
                "season": season,
                "id": game_id,
                "date": game["date"]["start"],
                "home_team": game["teams"]["home"]["name"],
                "away_team": game["teams"]["visitors"]["name"],
                "home_score": game["scores"]["home"]["points"],
                "away_score": game["scores"]["visitors"]["points"],
                "total_points": (
                    game["scores"]["home"]["points"] + game["scores"]["visitors"]["points"]
                    if game["scores"]["home"]["points"] is not None and game["scores"]["visitors"]["points"] is not None else None
                )
            }
            all_games.append(game_record)

            for player in player_stats:
                stat = player.get("statistics", {})
                player_record = {
                    "game_id": game_id,
                    "team": player.get("team", {}).get("name"),
                    "player": f"{player.get('player', {}).get('firstname', '')} {player.get('player', {}).get('lastname', '')}",
                    "points": stat.get("points"),
                    "rebounds": stat.get("totReb"),
                    "assists": stat.get("assists"),
                    "blocks": stat.get("blocks"),
                    "steals": stat.get("steals"),
                    "turnovers": stat.get("turnovers"),
                    "minutes": stat.get("min"),
                    "fg_pct": stat.get("fgp"),
                    "fg3_pct": stat.get("tpp"),
                    "ft_pct": stat.get("ftp"),
                }
                all_player_stats.append(player_record)

            time.sleep(RATE_LIMIT_DELAY)

    if all_games:
        pd.DataFrame(all_games).to_csv("nba_games_2021_2025.csv", index=False)
    if all_player_stats:
        pd.DataFrame(all_player_stats).to_csv("nba_player_stats_2021_2025.csv", index=False)

    print("✅ Done. CSVs saved.")

if __name__ == "__main__":
    main()

