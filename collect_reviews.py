import json

import requests

import time
import sys
import logging

import sqlite3
from pathlib import Path

API_URL = "https://api.steampowered.com/IUserReviewsService/GetAppReviews/v1/"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "steam.db"
APP_ID = 4115450 # 影之刃零


def fetch_page(app_id, cursor="*"):
    params = {
        "appid": app_id,
        "languages": ["schinese"], 
        "filter": 1, 
        "num_per_page": 100, 
        "cursor": cursor, 
    }
    resp = requests.get(API_URL, params={"input_json": json.dumps(params)}, timeout=15)
    resp.raise_for_status()
    return resp.json()["response"]


def fetch_with_retry(app_id, cursor, attempts=3, wait=10):
    for i in range(attempts):
        try:
            return fetch_page(app_id, cursor)
        except (requests.Timeout, requests.ConnectionError) as e:
            if i == attempts - 1:
                raise
            logging.warning(f"app_id {app_id}: 第 {i + 1} 次请求失败（{type(e).__name__}），{wait} 秒后重试")
            time.sleep(wait)


def save(con, app_id, reviews):
    rows = [
        (
            int(r["recommendationid"]), 
            app_id, 
            r["language"], 
            int(r["voted_up"]), 
            r["author"].get("playtime_at_review"), 
            r.get("votes_up"), 
            r["timestamp_created"], 
            r.get("review"),
        )
        for r in reviews
    ]
    before = con.total_changes
    con.executemany(
        "INSERT INTO review (recommendationid, app_id, language, voted_up,"
        " playtime_at_review, votes_up, created, review) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        " ON CONFLICT(recommendationid) DO NOTHING",
        rows,
    )
    con.commit()
    return con.total_changes - before


def collect(con, app_id, max_pages=5, stop_when_seen=True, cursor="*", cursor_file=None):
    total = 0
    n = 0
    reviews = []
    for page in range(max_pages):
        try:
            data = fetch_with_retry(app_id, cursor)
        except requests.HTTPError as e:
            if e.response is not None and e.response.statuscode == 429:
                logging.warning("被限流 (429)，进度已保存，过一阵再跑")
                break
            raise
        reviews = data.get("reviews", [])
        if not reviews:
            break
        n = save(con, app_id, reviews)
        total += n
        logging.info(f"app_id {app_id} 第 {page + 1} 页：{len(reviews)} 条，新增 {n}")
        if n == 0 and stop_when_seen:
            break
        if data["cursor"] == cursor:
            break
        cursor = data["cursor"]
        if cursor_file:
            cursor_file.write_text(cursor)
        time.sleep(2)
    else:
        if stop_when_seen and n == len(reviews):
            logging.warning(f"app_id {app_id} 翻满 {max_pages} 页且最后一页全是新评论，可能有遗漏")
    return total


def main():
    con = sqlite3.connect(DB_PATH, timeout=60)
    if len(sys.argv) > 1 and sys.argv[1] == "backfill":
        pages = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        cursor_file = BASE_DIR / "data" / f"review_cursor_{APP_ID}.txt"
        start = cursor_file.read_text() if cursor_file.exists() else "*"
        total = collect(con, APP_ID, max_pages=pages, stop_when_seen=False, cursor=start, cursor_file=cursor_file)
    else:
        total = collect(con, APP_ID)
    logging.info(f"评论采集结束，新增 {total} 条")
    con.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    main()
