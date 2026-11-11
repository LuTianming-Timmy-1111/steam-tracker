import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from common import OUT_DIR, load_reviews, setup_font


def main():
    df = load_reviews()
    df["date"] = df["bj"].dt.date
    daily = df.groupby("date").agg(count=("voted_up", "size"), pos_rate=("voted_up", "mean"))
    daily = daily.iloc[:-1]  # 备份在凌晨 4 点，最后一天不完整
    print(daily.round(3))
    setup_font()
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 7))
    ax1.bar(daily.index, daily["count"])
    ax1.set_title("影之刃零 每天新增简体中文评论数")
    ax2.plot(daily.index, daily["pos_rate"], marker="o")
    ax2.set_ylim(0.85, 1.0)
    ax2.set_title("每天好评率")
    ax2.xaxis.set_major_locator(mdates.DayLocator(tz="UTC"))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d", tz="UTC"))
    OUT_DIR.mkdir(exist_ok=True)
    fig.savefig(OUT_DIR / "07_review_daily.png", dpi=100)
    print("保存", OUT_DIR / "07_review_daily.png")


if __name__ == "__main__":
    main()
