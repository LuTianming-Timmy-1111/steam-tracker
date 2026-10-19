import logging
import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "steam.db"
BACKUP_DIR = BASE_DIR / "backups"
KEEP = 7


def main():
    BACKUP_DIR.mkdir(exist_ok=True)
    target = BACKUP_DIR / f"steam-{datetime.now():%Y%m%d}.db"

    src = sqlite3.connect(DB_PATH)
    dst = sqlite3.connect(target)
    src.backup(dst)
    dst.close()
    src.close()
    logging.info(f"备份完成 {target.name}，{target.stat().st_size} 字节")

    backups = sorted(BACKUP_DIR.glob("steam-*.db"))
    for old in backups[:-KEEP]:
        old.unlink()
        logging.info(f"删除旧备份 {old.name}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    main()
