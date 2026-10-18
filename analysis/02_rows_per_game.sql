-- 每款游戏的数据条数，用于检查采集是否完整
-- 用 COUNT(p.game_id) 而不是 COUNT(*)，没有数据的游戏才会显示 0
SELECT g.name AS 游戏, COUNT(p.game_id) AS 条数
FROM game g
LEFT JOIN player_count p ON p.game_id = g.id
GROUP BY g.id
ORDER BY g.id;
