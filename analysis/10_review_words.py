import re
from collections import Counter

import pandas as pd

import jieba

from common import load_reviews

STOPWORDS = {
    "游戏", "这个", "就是", "但是", "真的", "没有", "还是", "感觉", "一个", "什么",
    "可以", "因为", "所以", "觉得", "自己", "已经", "如果", "这样", "然后", "不是",
    "非常", "有点", "还有", "而且", "虽然", "现在", "时候", "这种", "一些", "知道",
    "玩家", "直接", "不能", "一样", "完全", "一下", "只能", "很多", "这么", "那个",
    "一点",
}


def tokenize(text):
    words = jieba.lcut(text or "")
    result = [ w.lower() for w in words ]
    return [
        w for w in result
        if len(w) >= 2
        and w not in STOPWORDS
        and re.fullmatch(r"[\u4e00-\u9fa5a-zA-Z]+", w)
    ]

def doc_freq(texts):
    counter = Counter()
    for text in texts:
        counter.update(set(tokenize(text)))
    return counter

def distinctive(a_c, a_n, b_c, b_n, min_n=50):
    rows = []
    for word, c in a_c.items():
        if c < min_n:
            continue
        rate_a = c / a_n
        rate_b = (b_c[word] + 1) / b_n
        rows.append((word, c, rate_a, rate_b))
    result = pd.DataFrame(rows, columns=["word", "n", "rate_a", "rate_b"])
    result["ratio"] = result["rate_a"] / result["rate_b"]
    return result.sort_values("ratio", ascending=False)


def main():
    df = load_reviews()
    neg = df[df["voted_up"] == 0]
    pos = df[df["voted_up"] == 1]
    neg_c = doc_freq(neg["review"])
    pos_c = doc_freq(pos["review"])
    
    print("\n=== 差评特有 ===")
    print(distinctive(neg_c, len(neg), pos_c, len(pos)).head(30).round(3))
    print("\n=== 好评特有 ===")
    print(distinctive(pos_c, len(pos), neg_c, len(neg)).head(30).round(3))


if __name__ == "__main__":
    main()
