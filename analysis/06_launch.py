import sqlite3
from pathlib import Path

import pandas as pd

import matplotlib.pyplot as plt
from matplotlib import font_manager

BASE_DIR = Path(__file__).resolve().parent.parent
BACKUP_DIR = BASE_DIR / "backups"
OUT_DIR = BASE_DIR / "analysis" / "output"
FONT_PATH = BASE_DIR / "fonts" / "simhei.ttf"

TARGET = "鬼武者：剑之道"
LAUNCH = "2026-10-25 10:00"

SQL = """
SELECT g.name, gg.name AS grp, p.collected_at, p.players
FROM player_count p
JOIN game g ON p.game_id = g.id
JOIN game_group gg ON g.group_id = gg.id
"""


def setup_font():
    font_manager.fontManager.addfont(FONT_PATH)
    name = font_manager.FontProperties(fname=FONT_PATH).get_name()
    plt.rcParams["font.family"] = name
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["timezone"] = "Asia/Shanghai"


def load():
    db = sorted(BACKUP_DIR.glob("steam-*.db"))[-1]
    con = sqlite3.connect(db)
    df = pd.read_sql(SQL, con)
    con.close()
    df["t"] = pd.to_datetime(df["collected_at"], utc=True).dt.tz_convert("Asia/Shanghai")
    df["players"] = df["players"].mask(df["players"] == 0)
    print("读取", db.name, len(df), "行")
    return df


def main():
    df = load()
    launch = pd.Timestamp(LAUNCH, tz="Asia/Shanghai")
    tgt = df[df["name"] == TARGET]
    after = tgt[tgt["t"] >= launch]
    print("发售后", len(after), "小时，峰值", after["players"].max())
    print("峰值时刻", after.loc[after["players"].idxmax(), "t"])
    setup_font()
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(12, 8))
    ax1.plot(tgt["t"], tgt["players"])
    ax1.axvline(launch, color="red", linestyle="--")
    ax1.set_title(f"{TARGET} 在线人数")
    ax1.set_ylim(bottom=0)

    souls = df[df["grp"] == "魂类"]
    base = souls[souls["t"] < launch].groupby("name")["players"].mean()
    ratio = souls.pivot_table(index="t", columns="name", values="players") / base
    for name in ratio.columns:
        ax2.plot(ratio.index, ratio[name], label=name)
    ax2.axhline(1, color="grey", linewidth=0.8)
    ax2.axvline(launch, color="red", linestyle="--")
    ax2.set_title("魂类：相对发售前均值")
    ax2.legend(fontsize=8, ncol=4)
    OUT_DIR.mkdir(exist_ok=True)
    fig.savefig(OUT_DIR / "06_launch.png", dpi=120)
    print("已保存", OUT_DIR / "06_launch.png")


if __name__ == "__main__":
    main()
