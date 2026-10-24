import json
import os
import shutil
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "logs" / "collect.log"
BACKUP_DIR = BASE_DIR / "backups"
STATE_FILE = BASE_DIR / "logs" / "health_state.json"

STALE_MINUTES = 90
ERROR_WINDOW_MINUTES = 60
BACKUP_HOUR = 5
MIN_FREE_PERCENT = 10


def read_log_lines():
    if not LOG_FILE.exists():
        return []
    return LOG_FILE.read_text(encoding="utf-8").splitlines()


def parse_time(line):
    return datetime.strptime(line[:19], "%Y-%m-%d %H:%M:%S")


def check_collect(now, lines):
    for line in reversed(lines):
        if "采集结束" in line:
            t = parse_time(line)
            age = (now - t).total_seconds() / 60
            if age > STALE_MINUTES:
                return "已经 {:.0f} 分钟没有完成采集（最后一次 {:%m-%d %H:%M}）".format(age, t)
            return None
    return "日志里找不到任何一次“采集结束”"


def check_errors(now, lines):
    count = 0
    for line in lines:
        if " ERROR " not in line:
            continue
        try:
            t = parse_time(line)
        except ValueError:
            continue
        if (now - t).total_seconds() / 60 <= ERROR_WINDOW_MINUTES:
            count += 1
    if count:
        return "最近 {} 分钟有 {} 条 ERROR".format(ERROR_WINDOW_MINUTES, count)
    return None


def check_backup(now):
    if now.hour < BACKUP_HOUR:
        return None
    today = BACKUP_DIR / "steam-{:%Y%m%d}.db".format(now)
    if not today.exists():
        return "今天的备份还没有生成：" + today.name
    return None


def check_disk():
    usage = shutil.disk_usage("/")
    free = usage.free / usage.total * 100
    if free < MIN_FREE_PERCENT:
        return "磁盘剩余 {:.1f}%".format(free)
    return None


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save_state(state):
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")


def send_mail(subject, body):
    user = os.environ.get("SMTP_USER")
    if not user:
        print("[未配置邮箱，只打印]", subject)
        print(body)
        return
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = os.environ["MAIL_TO"]
    with smtplib.SMTP_SSL("smtp.qq.com", 465, timeout=10) as s:
        s.login(user, os.environ["SMTP_PASS"])
        s.send_message(msg)
    print("已发送：", subject)


def main():
    now = datetime.now()
    lines = read_log_lines()
    results = {
        "collect": check_collect(now, lines),
        "errors": check_errors(now, lines),
        "backup": check_backup(now),
        "disk": check_disk(),
    }
    problems = {k: v for k, v in results.items() if v}
    old = load_state()

    new_keys = [k for k in problems if k not in old]
    fixed_keys = [k for k in old if k not in problems]

    stamp = now.strftime("%Y-%m-%d %H:%M")
    if new_keys:
        body = "\n".join("- " + problems[k] for k in problems)
        send_mail("❌ Steam 采集异常（{}）".format(stamp), body)
    if fixed_keys:
        body = "\n".join("- " + old[k] for k in fixed_keys)
        send_mail("✅ Steam 采集已恢复（{}）".format(stamp), "以下问题已恢复：\n" + body)

    save_state(problems)
    print(stamp, "问题：", list(problems) or "无")


if __name__ == "__main__":
    main()
