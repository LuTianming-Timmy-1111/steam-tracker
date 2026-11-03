import matplotlib.pyplot as plt
import pandas as pd

from common import OUT_DIR, load, setup_font

def prepare(df):
    df["collected_at"] = pd.to_datetime(df["collected_at"], utc=True)
    df["bj"] = df["collected_at"].dt.tz_convert("Asia/Shanghai")
    df["ratio"] = df["players"] / df.groupby("game")["players"].transform("mean")
    return df


def plot(df):
    groups = df["grp"].unique()
    times = df["bj"].drop_duplicates().sort_values()
    print("分组", list(groups), "时间点", len(times))
    fig, axes = plt.subplots(2, 2, figsize=(14, 8), sharex=True, sharey=True)
    for ax, grp in zip(axes.flat, groups):
        sub = df[df["grp"] == grp]
        wide = sub.pivot_table(index="bj", columns="game", values="ratio").reindex(times)
        wide.plot(ax=ax)
        ax.set_title(grp)
        ax.set_xlabel("")
    for i in range(len(groups), 4):
        axes.flat[i].axis("off")
        axes.flat[i - 2].tick_params(labelbottom=True, which="both")
    fig.supylabel("人数 / 当日均值")
    fig.tight_layout()
    OUT_DIR.mkdir(exist_ok=True)
    path = OUT_DIR / "03_hourly_curve.png"
    fig.savefig(path, dpi=100)
    print("保存", path)


def main():
    setup_font()
    df = prepare(load())
    plot(df)


if __name__ == "__main__":
    main()
