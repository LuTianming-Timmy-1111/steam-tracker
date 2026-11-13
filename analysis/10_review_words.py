import re
from collections import Counter

import jieba

from common import load_reviews

STOPWORDS = {
    "游戏", "这个", "就是", "但是", "真的", "没有", "还是", "感觉", "一个", "什么",
    "可以", "因为", "所以", "觉得", "自己", "已经", "如果", "这样", "然后", "不是",
    "非常", "有点", "还有", "而且", "虽然", "现在", "时候", "这种", "一些", "知道",
}


def tokenize(text):
    words = jieba.lcut(text or "")
    return [
        w for w in words
        if len(w) >= 2
        and w not in STOPWORDS
        and re.fullmatch(r"[\u4e00-\u9fa5a-zA-Z]+", w)
    ]


def main():
    df = load_reviews()
    neg = df[df["voted_up"] == 0]
    print("差评", len(neg), "条")

    counter = Counter()
    for text in neg["review"]:
        counter.update(tokenize(text))

    for word, n in counter.most_common(30):
        print(word, n)


if __name__ == "__main__":
    main()
