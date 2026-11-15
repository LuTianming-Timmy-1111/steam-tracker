import sys

from common import load_reviews


def main():
    if len(sys.argv) < 2:
        raise SystemExit("用法：peek.py 词")
    word = sys.argv[1]
    reviews = load_reviews()
    neg = reviews[reviews["voted_up"] == 0]
    matches = neg[neg["review"].str.contains(word, na=False)]
    print(f"差评中包含『{word}』：{len(matches)} 条")
    sample = matches.sample(min(3, len(matches)), random_state=0)
    for text in sample["review"]:
        print("-" * 40)
        print(text[:200])


if __name__ == "__main__":
    main()
