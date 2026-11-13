import pandas as pd

from common import load_reviews


def main():
    df = load_reviews()
    df["hours"] = df["playtime_at_review"] / 60
    
    df["bucket"] = pd.cut(
        df["hours"], 
        bins=[0, 2, 5, 10, 20, 1000],
        labels=["0-2", "2-5", "5-10", "10-20", "20+"],
    )

    df["date"] = df["bj"].dt.date
    cross = df.pivot_table(index="date", columns="bucket", values="voted_up", aggfunc="mean",)
    counts = df.pivot_table(index="date", columns="bucket", values="voted_up", aggfunc="size",)
    print(cross.round(3), counts) 
    
    
if __name__ == "__main__":
    main()
