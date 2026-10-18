CREATE TABLE IF NOT EXISTS game_group (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS game (
    id           INTEGER PRIMARY KEY,
    app_id       INTEGER NOT NULL UNIQUE,
    name         TEXT NOT NULL,
    group_id     INTEGER NOT NULL REFERENCES game_group(id),
    release_date TEXT                -- 'YYYY-MM-DD'，可为空
);

CREATE TABLE IF NOT EXISTS player_count (
    game_id      INTEGER NOT NULL REFERENCES game(id),
    collected_at TEXT NOT NULL,      -- UTC，取整到小时
    players      INTEGER NOT NULL,
    PRIMARY KEY (game_id, collected_at)
);
