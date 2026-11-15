import sys

from common import load_reviews


def main():
    if len(sys.argv) < 2:
        raise SystemExit("用法：peek.py 词 [pos]")
    word = sys.argv[1]
    label = "好评" if len(sys.argv) > 2 and sys.argv[2] == "pos" else "差评"
    reviews = load_reviews()
    vote = 1 if label == "好评" else 0
    group = reviews[reviews["voted_up"] == vote]
    matches = group[group["review"].str.contains(word, na=False)]
    print(f"{label}中包含『{word}』：{len(matches)} 条")
    sample = matches.sample(min(3, len(matches)), random_state=0)
    for text in sample["review"]:
        print("-" * 40)
        print(text[:200])


if __name__ == "__main__":
    main()
