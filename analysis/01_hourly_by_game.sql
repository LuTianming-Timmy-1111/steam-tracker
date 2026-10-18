-- 每款游戏每小时的在线人数，按北京时间显示
SELECT gg.name AS 分组,
       g.name AS 游戏,
       datetime(p.collected_at, '+8 hours') AS 北京时间,
       p.players AS 在线人数
FROM player_count p
JOIN game g ON p.game_id = g.id
JOIN game_group gg ON g.group_id = gg.id
ORDER BY g.id, p.collected_at;
