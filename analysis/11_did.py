import numpy as np

from datetime import date

from common import load

GROUPS = {
    "鬼泣5": "动作", "剑星": "动作", "浪人崛起": "动作",
    "艾尔登法环": "魂类", "黑神话：悟空": "魂类", "匹诺曹的谎言": "魂类", "黑暗之魂3": "魂类",
    "明末：渊虚之羽": "魂类", "卧龙：苍天陨落": "魂类", "仁王2": "魂类",
    "生化危机9：安魂曲": "对照", "刺客信条：大革命": "对照", "极限竞速：地平线6": "对照",
}


def main():
    df = load()
    missing = set(GROUPS) - set(df["game"].unique())
    assert not missing, f"GROUPS 里这些游戏名在数据里找不到：{missing}"
    df["did_grp"] = df["game"].map(GROUPS)
    df = df.dropna(subset=["did_grp"])
    df["date"] = df["bj"].dt.date
    daily = df.groupby(["did_grp", "game", "date"])["players"].mean().reset_index()
    daily["log_p"] = np.log(daily["players"])

    pre = daily[(daily["date"] >= date(2026, 10, 19)) & (daily["date"] <= date(2026, 10, 28))]
    base = pre.groupby("game")["log_p"].mean()
    daily["rel"] = daily["log_p"] - daily["game"].map(base)

    daily = daily[(daily["date"] >= date(2026, 10, 19)) & (daily["date"] < daily["date"].max())]
    curve = daily.groupby(["date", "did_grp"])["rel"].mean().unstack()
    print(curve.round(3))


if __name__ == "__main__":
    main()
