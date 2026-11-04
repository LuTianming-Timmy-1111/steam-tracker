import pandas as pd

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from common import OUT_DIR, load, setup_font

TARGET = "影之刃零"
LAUNCH = "2026-10-29 10:00"


def main():
    df = load()
    launch = pd.Timestamp(LAUNCH, tz="Asia/Shanghai")
    tgt = df[df["game"] == TARGET]
    after = tgt[tgt["bj"] >= launch]
    print("发售后", len(after), "小时，峰值", after["players"].max())
    print("峰值时刻", after.loc[after["players"].idxmax(), "bj"])
    setup_font()
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(12, 8))
    ax1.plot(tgt["bj"], tgt["players"])
    ax1.axvline(launch, color="red", linestyle="--")
    ax1.set_title(f"{TARGET} 在线人数")
    ax1.set_ylim(bottom=0)

    souls = df[df["grp"] == "魂类"]
    base = souls[souls["bj"] < launch].groupby("game")["players"].mean()
    ratio = souls.pivot_table(index="bj", columns="game", values="players") / base
    for name in ratio.columns:
        ax2.plot(ratio.index, ratio[name], label=name)
    ax2.axhline(1, color="grey", linewidth=0.8)
    ax2.axvline(launch, color="red", linestyle="--")
    ax2.set_title("魂类：相对发售前均值")
    ax2.legend(fontsize=8, ncol=4)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    OUT_DIR.mkdir(exist_ok=True)
    fig.savefig(OUT_DIR / "06_launch.png", dpi=120)
    print("已保存", OUT_DIR / "06_launch.png")


if __name__ == "__main__":
    main()
