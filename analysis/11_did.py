import numpy as np

from common import load

GROUPS = {
    "鬼泣5": "动作", "剑星": "动作", "浪人崛起": "动作",
    "艾尔登法环": "魂类", "黑神话：悟空": "魂类", "匹诺曹的谎言": "魂类", "黑暗之魂3": "魂类",
    "明末：渊虚之羽": "魂类", "卧龙：苍天陨落": "魂类", "仁王2": "魂类",
    "生化危机9：安魂曲": "对照", "刺客信条：大革命": "对照", "极限竞速：地平线6": "对照",
}


def main():
    df = load()
    df["did_grp"] = df["game"].map(GROUPS)
    df = df.dropna(subset=["did_grp"])
    print(df["did_grp"].value_counts())


if __name__ == "__main__":
    main()
