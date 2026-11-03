import matplotlib.pyplot as plt
import pandas as pd

from common import OUT_DIR, load, setup_font

def prepare(df):
    df["bj"] = pd.to_datetime(df["collected_at"], utc=True).dt.tz_convert("Asia/Shanghai")
    df["date"] = df["bj"].dt.date
    df["hour"] = df["bj"].dt.hour
    df["weekend"] = df["bj"].dt.dayofweek >= 5
    n = df.groupby(["game", "date"])["players"].transform("size")
    df = df[n == 24].copy()
    df["ratio"] = df["players"] / df.groupby("game")["players"].transform("mean")
    days = df.drop_duplicates("date")
    print("完整的天：工作日", (~days["weekend"]).sum(), "天，周末", days["weekend"].sum(), "天")
    return df


def plot(df):
    groups = df["grp"].unique()
    fig, axes = plt.subplots(2, 2, figsize=(14, 8), sharex=True, sharey=True)
    for ax, grp in zip(axes.flat, groups):
        sub = df[df["grp"] == grp]
        for flag, label in [(False, "工作日"), (True, "周末")]:
            part = sub[sub["weekend"] == flag]
            if part.empty:
                continue
            curve = part.groupby("hour")["ratio"].mean()
            ax.plot(curve.index, curve.values, marker="o", label=label)
        ax.axhline(1, color="gray", linewidth=0.8, linestyle="--")
        ax.set_title(grp)
        ax.set_xticks(range(0, 24, 3))
        ax.legend()
    for i in range(len(groups), 4):
        axes.flat[i].axis("off")
        axes.flat[i - 2].tick_params(labelbottom=True, which="both")
    fig.supxlabel("几点钟（北京时间）")
    fig.supylabel("人数 / 该游戏均值")
    fig.tight_layout()
    OUT_DIR.mkdir(exist_ok=True)
    path = OUT_DIR / "05_hour_of_day.png"
    fig.savefig(path, dpi=100)
    print("保存", path)


def main():
    setup_font()
    df = prepare(load())
    plot(df)


if __name__ == "__main__":
    main()
