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
        batch = res.json()["response"]
        if not batch: break
        games.extend(batch)
        page += 1
        time.sleep(RATE_LIMIT_DELAY)
    return games

def get_player_stats(game_id):
    url = f"https://api-nba-v1.p.rapidapi.com/players/statistics?game={game_id}"
    res = requests.get(url, headers=HEADERS)
    return res.json()["response"]

games_data = []
player_data = []

teams = get_teams()
time.sleep(RATE_LIMIT_DELAY)

for season in SEASONS:
    print(f"📅 Season {season}")
    games = get_games_by_season(season)
    
    for game in games:
        if not game["scores"]["home"]["points"] or not game["scores"]["visitors"]["points"]:
            continue

        g = {
            "season": season,
            "date": game["date"]["start"][:10],
            "home_team": game["teams"]["home"]["name"],
            "away_team": game["teams"]["visitors"]["name"],
            "home_score": game["scores"]["home"]["points"],
            "away_score": game["scores"]["visitors"]["points"],
            "total_points": game["scores"]["home"]["points"] + game["scores"]["visitors"]["points"]
        }
        games_data.append(g)

        stats = get_player_stats(game["id"])
        for p in stats:
            player = {
                "game_id": game["id"],
                "season": season,
                "team": p["team"]["name"],
                "player": f"{p['player']['firstname']} {p['player']['lastname']}",
                "points": p["points"],
                "rebounds": p["totReb"],
                "assists": p["assists"],
                "minutes": p["min"],
                "fgp": p["fgp"],
                "tpp": p["tpp"],
                "ftp": p["ftp"],
                "plus_minus": p["plusMinus"]
            }
            player_data.append(player)

        time.sleep(RATE_LIMIT_DELAY)

# Save as CSV
pd.DataFrame(games_data).to_csv("nba_games_2021_2025.csv", index=False)
pd.DataFrame(player_data).to_csv("nba_player_stats_2021_2025.csv", index=False)

print("✅ Done. CSVs saved.")
