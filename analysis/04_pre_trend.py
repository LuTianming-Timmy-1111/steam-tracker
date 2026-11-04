import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from common import LAUNCH, OUT_DIR, load, setup_font

# 赛博朋克2077：10/20 动画第二季首播、10/22 更新 2.5、Steam 7 折至 10/26，10/23 起人数暴涨，与影之刃零无关
# 鬼武者：剑之道：发售一个多月，处于自身衰退期
EXCLUDE = {"赛博朋克2077", "鬼武者：剑之道"}

def daily_ratio(df):
    df["date"] = df["bj"].dt.date
    n = df.groupby(["game", "date"])["players"].transform("size")
    full = df[n == 24]
    daily = full.groupby(["grp", "game", "date"])["players"].mean().reset_index()
    daily["ratio"] = daily["players"] / daily.groupby("game")["players"].transform("mean")
    return daily


def plot(by_grp):
    ax = by_grp.plot(marker="o", figsize=(10, 5))
    ax.axhline(1, color="gray", linewidth=0.8, linestyle="--")
    ax.xaxis.set_major_locator(mdates.DayLocator(tz="UTC"))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d", tz="UTC"))
    ax.set_title("各组日均人数（仅完整的天，以各游戏自身均值归一化）")
    ax.set_xlabel("日期（北京时间）")
    ax.set_ylabel("日均人数 / 均值")
    OUT_DIR.mkdir(exist_ok=True)
    path = OUT_DIR / "04_pre_trend.png"
    plt.savefig(path, dpi=100)
    print("保存", path)


def main():
    setup_font()
    df = load()
    df = df[df["bj"] < LAUNCH]
    df = df[~df["game"].isin(EXCLUDE)]
    daily = daily_ratio(df)
    by_grp = daily.pivot_table(index="date", columns="grp", values="ratio")
    print(by_grp.round(3))
    plot(by_grp)


if __name__ == "__main__":
    main()
