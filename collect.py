import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

DB_PATH = Path("data/steam.db")
API_URL = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"


def fetch_players(app_id):
    resp = requests.get(API_URL, params={"appid": app_id}, timeout=10)
    data = resp.json()["response"]
    if data.get("result") != 1:
        return None
    return data["player_count"]


def main():
    now = datetime.now(timezone.utc)
    collected_at = now.replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
    print("采集时间（UTC）：", collected_at)

    con = sqlite3.connect(DB_PATH)
    games = con.execute("SELECT id, app_id, name FROM game ORDER BY id").fetchall()
    con.close()

    for game_id, app_id, name in games:
        time.sleep(1)
        try:
            players = fetch_players(app_id)
        except requests.RequestException as e:
            print(f"{name}: 请求失败，跳过（{e}）")
            continue
        if players is None:
            print(f"{name}: 暂无数据，跳过")
            continue
        print(f"{name}: {players}")


if __name__ == "__main__":
    main()
