import sqlite3
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager

BASE_DIR = Path(__file__).resolve().parent.parent
BACKUP_DIR = BASE_DIR / "backups"
OUT_DIR = BASE_DIR / "analysis" / "output"
FONT_PATH = BASE_DIR / "fonts" / "simhei.ttf"

SQL = """
SELECT g.name AS game, gg.name AS grp, p.collected_at, p.players
FROM player_count p
JOIN game g ON p.game_id = g.id
JOIN game_group gg ON g.group_id = gg.id
"""


def setup_font():
    font_manager.fontManager.addfont(FONT_PATH)
    name = font_manager.FontProperties(fname=FONT_PATH).get_name()
    plt.rcParams["font.family"] = name


def load():
    db = sorted(BACKUP_DIR.glob("steam-*.db"))[-1]
    con = sqlite3.connect(db)
    df = pd.read_sql(SQL, con)
    con.close()
    print("读取", db.name, len(df), "行")
    return df


def daily_ratio(df):
    df["bj"] = pd.to_datetime(df["collected_at"], utc=True).dt.tz_convert("Asia/Shanghai")
    df["date"] = df["bj"].dt.date
    n = df.groupby(["game", "date"])["players"].transform("size")
    full = df[n == 24]
    daily = full.groupby(["grp", "game", "date"])["players"].mean().reset_index()
    daily["ratio"] = daily["players"] / daily.groupby("game")["players"].transform("mean")
    return daily


def plot(by_grp):
    ax = by_grp.plot(marker="o", figsize=(10, 5))
    ax.axhline(1, color="gray", linewidth=0.8, linestyle="--")
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    ax.set_title("各组日均人数（仅完整的天，以各游戏自身均值归一化）")
    ax.set_xlabel("日期（北京时间）")
    ax.set_ylabel("日均人数 / 均值")
    OUT_DIR.mkdir(exist_ok=True)
    path = OUT_DIR / "04_pre_trend.png"
    plt.savefig(path, dpi=100)
    print("保存", path)


def main():
    setup_font()
    daily = daily_ratio(load())
    by_grp = daily.pivot_table(index="date", columns="grp", values="ratio")
    print(by_grp.round(3))
    plot(by_grp)


if __name__ == "__main__":
    main()
