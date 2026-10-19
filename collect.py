import logging
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "steam.db"
API_URL = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"


def fetch_players(app_id):
    resp = requests.get(API_URL, params={"appid": app_id}, timeout=10)
    data = resp.json()["response"]
    if data.get("result") != 1:
        return None
    return data["player_count"]


def fetch_with_retry(app_id, attempts=3, wait=5):
    for i in range(attempts):
        try:
            return fetch_players(app_id)
        except requests.RequestException as e:
            if i == attempts - 1:
                raise
            logging.warning(f"app_id {app_id}: 第 {i + 1} 次失败（{type(e).__name__}），{wait} 秒后重试")
            time.sleep(wait)


def main():
    now = datetime.now(timezone.utc)
    collected_at = now.replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"开始采集，collected_at = {collected_at} UTC")

    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    games = con.execute("SELECT id, app_id, name FROM game ORDER BY id").fetchall()

    saved = 0
    for game_id, app_id, name in games:
        time.sleep(1)
        try:
            players = fetch_with_retry(app_id)
        except requests.RequestException as e:
            logging.error(f"{name}: 请求失败，跳过（{type(e).__name__}）")
            continue
        if players is None:
            logging.info(f"{name}: 暂无数据，跳过")
            continue
        logging.info(f"{name}: {players}")
        cur = con.execute(
            "INSERT OR IGNORE INTO player_count (game_id, collected_at, players) VALUES (?, ?, ?)",
            (game_id, collected_at, players),
        )
        saved += cur.rowcount

    con.commit()
    con.close()
    logging.info(f"采集结束，写入 {saved} 条")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    main()
