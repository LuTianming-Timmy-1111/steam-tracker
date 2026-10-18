import sqlite3
from pathlib import Path

DB_PATH = Path("data/steam.db")
SCHEMA_PATH = Path("schema.sql")


def main():
    DB_PATH.parent.mkdir(exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

    tables = con.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
    ).fetchall()
    print(tables)
    con.close()


if __name__ == "__main__":
    main()
