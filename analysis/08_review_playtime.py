import pandas as pd

from common import load_reviews


def main():
    df = load_reviews()
    df["hours"] = df["playtime_at_review"] / 60

    df["bucket"] = pd.cut(
        df["hours"],
        bins=[0, 2, 5, 10, 20, 1000],
        labels=["0-2", "2-5", "5-10", "10-20", "20+"],
        include_lowest=True,
    )

    result = df.groupby("bucket").agg(
        count=("voted_up", "size"),
        pos_rate=("voted_up", "mean"),
    )

    print(result.round(3))


if __name__ == "__main__":
    main()
