import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
BACKUP_DIR = BASE_DIR / "backups"
OUT_DIR = BASE_DIR / "analysis" / "output"


def load():
    db = sorted(BACKUP_DIR.glob("steam-*.db"))[-1]
    con = sqlite3.connect(db)
    df = pd.read_sql("SELECT * FROM player_count", con)
    con.close()
    print("读取", db.name, len(df), "行")
    return df


def prepare(df):
    df["collected_at"] = pd.to_datetime(df["collected_at"], utc=True)
    df["bj"] = df["collected_at"].dt.tz_convert("Asia/Shanghai")
    df["ratio"] = df["players"] / df.groupby("game_id")["players"].transform("mean")
    return df.pivot_table(index="bj", columns="game_id", values="ratio")


def plot(wide):
    ax = wide.plot(figsize=(12, 6))
    ax.set_xlabel("time (Beijing)")
    ax.set_ylabel("players / daily mean")
    OUT_DIR.mkdir(exist_ok=True)
    path = OUT_DIR / "03_hourly_curve.png"
    plt.savefig(path, dpi=100)
    print("保存", path)


def main():
    df = load()
    wide = prepare(df)
    print(wide.shape)
    plot(wide)


if __name__ == "__main__":
    main()
