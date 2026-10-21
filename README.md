# steam-tracker

每小时采集 17 款 Steam 游戏的同时在线人数，存入 SQLite。游戏以类魂和动作类为主，另有几款不同类型的 3A 大作作为参照。

主要用途：以影之刃零（2026-10-29 发售）为例，观察它发售前后，同类游戏与其他游戏的在线人数变化有何不同。采集从 2026-10-18 开始，发售前约有 10 天的基线数据。

数据来源：Steam Web API `ISteamUserStats/GetNumberOfCurrentPlayers`，无需 API key。

## 分组

| 分组 | 选入原因 |
|---|---|
| 新作 | 影之刃零本身，发售前接口无数据 |
| 魂类 | 与影之刃零战斗系统相近的类魂游戏 |
| 动作 | 强调连招、节奏的动作游戏 |
| 3A | 不同类型的大作，用作参照 |

分组只是选入时的粗略标签。一款游戏往往同时属于多种类型（例如只狼既是 3A，也是快节奏的剑戟动作），分析时的处理组与对照组按具体问题另行挑选，不以此分组为准。

## 追踪的游戏

| 分组 | 游戏 | AppID |
|---|---|---|
| 3A | 生化危机9：安魂曲 | 3764200 |
| 3A | 赛博朋克2077 | 1091500 |
| 3A | 只狼：影逝二度 | 814380 |
| 3A | 刺客信条：大革命 | 289650 |
| 3A | 极限竞速：地平线6 | 2483190 |
| 魂类 | 艾尔登法环 | 1245620 |
| 魂类 | 黑神话：悟空 | 2358720 |
| 魂类 | 匹诺曹的谎言 | 1627720 |
| 魂类 | 黑暗之魂3 | 374320 |
| 魂类 | 明末：渊虚之羽 | 2277560 |
| 魂类 | 卧龙：苍天陨落 | 1448440 |
| 魂类 | 仁王2 | 1325200 |
| 新作 | 影之刃零 | 4115450 |
| 动作 | 鬼泣5 | 601150 |
| 动作 | 剑星 | 3489700 |
| 动作 | 浪人崛起 | 1340990 |
| 动作 | 鬼武者：剑之道 | 2638890 |

游戏列表维护在 `init_db.py` 的 `GAMES` 中。新增分组或游戏只能追加在列表末尾，以保持各环境中 `id` 一致。

## 数据

数据库为 `data/steam.db`（SQLite，不进 Git），建表语句见 `schema.sql`。

| 表 | 内容 |
|---|---|
| `game_group` | 分组 |
| `game` | 游戏：Steam AppID、名称、分组、发售日期（可空） |
| `player_count` | 在线人数，主键为 `(game_id, collected_at)`，每款游戏每小时一条 |

约定：

- `collected_at` 为 **UTC** 时间，取整到小时，格式 `YYYY-MM-DD HH:00:00`。查询时可用 `datetime(collected_at, '+8 hours')` 换算为北京时间。
- 每小时第 5 分钟采集。Steam 接口有数分钟的缓存，数值是近似的时点快照。
- 接口无数据（如发售前的影之刃零，返回 `result: 42`）或三次请求均失败时，该小时**不插入**记录，以缺行表示缺数据。
- 同一小时重复采集时保留首次写入的值（`INSERT OR IGNORE`），可在第 35 分钟补采失败的游戏。

查询示例：艾尔登法环的在线人数，按北京时间显示

```sql
SELECT g.name, datetime(p.collected_at, '+8 hours') AS 北京时间, p.players
FROM player_count p JOIN game g ON p.game_id = g.id
WHERE g.app_id = 1245620
ORDER BY p.collected_at;
```

## 部署

环境：Ubuntu 24.04，Python 3.12。

```bash
git clone https://github.com/LuTianming-Timmy-1111/steam-tracker.git
cd steam-tracker
apt install python3.12-venv          # Ubuntu 默认未安装，否则无法创建 venv
python3 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/python init_db.py           # 建表并录入游戏，可重复执行
```

定时任务（`crontab -e`，时间按服务器时区，路径按实际位置修改）：

```
5,35 * * * * /root/steam-tracker/run_collect.sh
20 4 * * * /root/steam-tracker/run_backup.sh
```

| 入口脚本 | 作用 | 日志 |
|---|---|---|
| `run_collect.sh` | 采集一次；第 35 分钟的运行用于补采 | `logs/collect.log` |
| `run_backup.sh` | 用 SQLite 备份接口复制数据库到 `backups/`，保留最近 7 份 | `logs/backup.log` |

入口脚本会先切换到项目目录，并直接调用 `venv/bin/python`，因此 cron 中无需激活虚拟环境。

检查运行状态：

```bash
tail -20 logs/collect.log
grep -c ERROR logs/collect.log       # 正常应为 0
```

## 开发

代码在开发环境修改，经 GitHub 同步到服务器。服务器上只执行 `git pull`，不直接改代码。开发环境使用与服务器相同的 Python 3.12（例如 `python:3.12-slim` 容器），避免版本差异。

服务器更新：

```bash
cd ~/steam-tracker
git pull
venv/bin/python init_db.py           # 仅当游戏列表有变化时需要
```

`venv/`、`data/`、`logs/`、`backups/` 均不进 Git，`git pull` 不会影响已有数据。

## 文件

| 文件 | 说明 |
|---|---|
| `schema.sql` | 建表语句 |
| `init_db.py` | 建表，录入分组和游戏 |
| `collect.py` | 采集：失败重试 3 次，无数据或仍失败则跳过该游戏 |
| `backup.py` | 备份数据库，保留最近 7 份 |
| `run_collect.sh`、`run_backup.sh` | cron 调用的入口脚本 |
| `requirements.txt` | Python 依赖，版本固定 |

## 分析

分析在开发环境进行，读取 `backups/` 中最新的一份备份，不直接访问服务器上的数据库。

```bash
venv/bin/pip install -r requirements-analysis.txt
venv/bin/python analysis/03_hourly_curve.py
```

图中的中文需要字体：将中文 TrueType 字体放在 `fonts/simhei.ttf`（脚本按此文件名读取）。`fonts/` 与 `analysis/output/` 均不进 Git。

| 文件 | 说明 |
|---|---|
| `analysis/01_hourly_by_game.sql` | 各游戏每小时人数（北京时间） |
| `analysis/02_rows_per_game.sql` | 各游戏已采集条数 |
| `analysis/03_hourly_curve.py` | 各游戏人数随时间的变化，以各自均值归一化，按分组分图 |
| `analysis/04_pre_trend.py` | 发售前各组日均人数（仅完整的天），用于检查平行趋势 |

归一化以采集期内的均值为分母，数据增加后图形会随之变化。数据不足一周时，日内作息与星期效应无法区分。
