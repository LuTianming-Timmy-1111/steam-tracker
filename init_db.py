import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "steam.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"

GROUPS = ["3A", "魂类", "新作", "动作"]

GAMES = [
    # (app_id, 名称, 分组, 发售日期)
    (3764200, "生化危机9：安魂曲", "3A", None),
    (1091500, "赛博朋克2077", "3A", None),
    (814380, "只狼：影逝二度", "3A", None),
    (289650, "刺客信条：大革命", "3A", None),
    (2483190, "极限竞速：地平线6", "3A", None),
    (1245620, "艾尔登法环", "魂类", None),
    (2358720, "黑神话：悟空", "魂类", None),
    (1627720, "匹诺曹的谎言", "魂类", None),
    (374320, "黑暗之魂3", "魂类", None),
    (4115450, "影之刃零", "新作", "2026-10-29"),
    (2277560, "明末：渊虚之羽", "魂类", None),
    (1448440, "卧龙：苍天陨落", "魂类", None),
    (1325200, "仁王2", "魂类", None),
    (601150, "鬼泣5", "动作", None),
    (3489700, "剑星", "动作", None),
    (1340990, "浪人崛起", "动作", None),
    (2638890, "鬼武者：剑之道", "动作", None),
]


def seed(con):
    con.executemany(
        "INSERT OR IGNORE INTO game_group (name) VALUES (?)",
        [(g,) for g in GROUPS],
    )
    for app_id, name, group, release_date in GAMES:
        con.execute(
            """
            INSERT OR IGNORE INTO game (app_id, name, group_id, release_date)
            VALUES (?, ?, (SELECT id FROM game_group WHERE name = ?), ?)
            """,
            (app_id, name, group, release_date),
        )
    con.commit()


def main():
    DB_PATH.parent.mkdir(exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    seed(con)

    rows = con.execute(
        """
        SELECT gg.name, g.app_id, g.name, g.release_date
        FROM game g JOIN game_group gg ON g.group_id = gg.id
        ORDER BY gg.id, g.id
        """
    ).fetchall()
    for row in rows:
        print(row)
    print("共", len(rows), "款")
    con.close()


if __name__ == "__main__":
    main()
