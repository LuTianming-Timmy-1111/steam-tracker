import sqlite3
from pathlib import Path

import pandas as pd

import matplotlib.pyplot as plt
from matplotlib import font_manager

BASE_DIR = Path(__file__).resolve().parent.parent
BACKUP_DIR = BASE_DIR / "backups"
OUT_DIR = BASE_DIR / "analysis" / "output"
FONT_PATH = BASE_DIR / "fonts" / "simhei.ttf"
LAUNCH = pd.Timestamp("2026-10-29 10:00", tz="Asia/Shanghai")

SQL = """
SELECT g.name AS game, gg.name AS grp, p.collected_at, p.players
FROM player_count p
JOIN game g ON p.game_id = g.id
JOIN game_group gg ON g.group_id = gg.id
"""

SQL_REVIEWS = """
SELECT r.recommendationid, g.name AS game, r.voted_up,
       r.playtime_at_review, r.votes_up, r.created, r.review
FROM review r
JOIN game g ON r.app_id = g.app_id
"""


def latest_backup():
    dbs = sorted(BACKUP_DIR.glob("steam-*.db"))
    if not dbs:
        raise SystemExit(f"{BACKUP_DIR} 里没有 steam-*.db，先从 Windows 传一份备份过来")
    return dbs[-1]


def load():
    db = latest_backup()
    con = sqlite3.connect(db)
    df = pd.read_sql(SQL, con)
    con.close()
    df["bj"] = pd.to_datetime(df["collected_at"], utc=True).dt.tz_convert("Asia/Shanghai")
    df["players"] = df["players"].mask(df["players"] == 0)
    print("读取", db.name, len(df), "行")
    return df


def load_reviews():
    db = latest_backup()
    con = sqlite3.connect(db)
    df = pd.read_sql(SQL_REVIEWS, con)
    con.close()
    df["bj"] = pd.to_datetime(df["created"], unit="s", utc=True).dt.tz_convert("Asia/Shanghai")
    print("读取", db.name, len(df), "条评论")
    return df


def setup_font():
    font_manager.fontManager.addfont(FONT_PATH)
    name = font_manager.FontProperties(fname=FONT_PATH).get_name()
    plt.rcParams["font.family"] = name
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["timezone"] = "Asia/Shanghai"

