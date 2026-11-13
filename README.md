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
| `review` | 简体中文评论，主键为 `recommendationid`；含 AppID、语言、是否好评（1/0）、写评论时的游戏时长（分钟）、觉得有用的人数、发布时间（Unix 时间戳，UTC）、正文 |

约定：

- `collected_at` 为 **UTC** 时间，取整到小时，格式 `YYYY-MM-DD HH:00:00`。查询时可用 `datetime(collected_at, '+8 hours')` 换算为北京时间。
- 每小时第 5 分钟采集。Steam 接口有数分钟的缓存，数值是近似的时点快照。
- 接口无数据（如发售前的影之刃零，返回 `result: 42`）、返回 0 人（接口偶发异常，几款游戏同时归零），或三次请求均失败时，该小时**不插入**记录，以缺行表示缺数据。
- 同一小时重复采集时保留首次写入的值（`INSERT OR IGNORE`），可在第 35 分钟补采失败的游戏。
- 评论每小时第 25 分钟增量采集：从最新翻起，一整页都已存过就停。补历史用 `run_reviews.sh backfill 页数`，进度存在 `data/review_cursor_<AppID>.txt`，中断后可接着翻。
- 评论用 `INSERT ... ON CONFLICT(recommendationid) DO NOTHING` 去重：只跳过重复的评论，其他约束错误照常报错。

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
| `collect_reviews.py` | 评论采集：每日增量 / 补历史（断点续翻）；超时和连接错误重试 3 次，429 限流时保存进度退出 |
| `health_check.py` | 健康检查：采集停滞超过 90 分钟、近 60 分钟有 ERROR、05:00 后没有当天备份、磁盘剩余不足 10%，有新问题或恢复时发邮件 |
| `run_reviews.sh`、`run_health.sh` | cron 调用的入口脚本 |
| `analysis/` | 分析脚本，公共函数在 `common.py`；03–06 在线人数，07–09 评论 |
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
| `analysis/05_hour_of_day.py` | 按几点钟的人数规律，工作日与周末分开（仅完整的天） |

归一化以采集期内的均值为分母，数据增加后图形会随之变化。数据不足一周时，日内作息与星期效应无法区分。

## 评论分析：影之刃零（简体中文）

脚本：`analysis/07_review_daily.py`（每天）、`08_review_playtime.py`（按时长）、`09_review_day_playtime.py`（日期 × 时长）。

### 数据范围

- 发售日 10/29 至 11/12 的简体中文评论，共 90,399 条，整体好评率约 95%
- 按接口默认设置：只含 Steam 购买的评论，排除了被 Steam 判定为刷评的评论；已删除的评论不在内
- `playtime_at_review`：写评论时的游戏时长（分钟）

结论只适用于这个范围。

### 每天的好评率

发售当天好评率最低，约 88%；之后逐日上升，到 11/03 前后稳定在 97% 左右。

### 写评论时的游戏时长

| 时长 | 评论数 | 好评率 |
|---|---|---|
| 0–2 小时 | 2,342 | 66.5% |
| 2–5 小时 | 7,550 | 91.3% |
| 5–10 小时 | 11,883 | 93.3% |
| 10–20 小时 | 17,862 | 95.8% |
| 20 小时以上 | 50,762 | 97.1% |

时长越长，好评率越高。玩不到 2 小时就写评论的人，约三分之一给了差评。

0–2 小时差评偏多的可能原因（推测，数据无法区分）：

- 受宣发影响冲动购买，发现不是自己喜欢的类型
- 首发的技术问题（闪退、卡顿）在开头就劝退
- 前期流程、难度和玩法展示不如后期（结合个人游玩体验）
- 2 小时正好是 Steam 的退款门槛，不满意的玩家可能退款并留下差评

时长和好评率的正相关，**不能直接说明“游戏后期更好玩”**：也可能是喜欢这款游戏的玩家才玩得更久，不喜欢的玩家玩不下去、时长短、评分也低（反向因果）。两种情况可能同时存在。

### 两者叠加

发售初期，写评论的玩家时长结构随日期快速变化：10/29 大多只玩了几个小时，11/02 之后以 20 小时以上为主。评分又随时长升高，所以每天好评率的上升，**相当一部分可以由时长结构的变化解释**。

在同一时长档内比较，发售头几天好评率仍有上升（2–5 小时：91.6% → 94.9%，10/29 → 11/03；10–20 小时：93.2% → 96.8%，10/29 → 11/02），之后基本持平。**提示**除了时长，可能还有别的因素，比如补丁修复、早期和后期买家的差异。

`20+` 小时档 10/29 的数据不可靠（见下），没有用来作证据。

### 待验证

- 10/29 发售当天，有 1,682 条评论的时长已超过 20 小时。推测大多是玩家后来**修改过评论**、`playtime_at_review` 记的是修改时的时长；也可能有一部分是提前拿到游戏的媒体或主播。需要另存 `timestamp_updated` 才能区分
- 评分与时长的正相关里，有多少来自游戏前后期的内容差异（因果），有多少来自玩家的自我选择
- 时长结构具体能解释每天好评率上升的多少
