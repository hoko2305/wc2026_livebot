import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.espn import fetch_scoreboard
from utils.telegram import send_message
from utils.kv import redis_get, redis_set

TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
TELEGRAM_GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")

def handler(request):
    # 1. 抓取 ESPN 数据
    games = fetch_scoreboard()
    if not games:
        return {"status": "no data"}

    # 2. 从 KV 获取上次数据
    last_games_json = redis_get("scoreboard")
    last_games = json.loads(last_games_json) if last_games_json else []

    # 3. 检测事件（简化：比分变化即推送）
    for game in games:
        game_id = game['game_id']
        last_game = next((g for g in last_games if g['game_id'] == game_id), None)
        if last_game and (last_game['home_score'] != game['home_score'] or last_game['away_score'] != game['away_score']):
            msg = f"⚽ 比分更新！\n{game['home_team']} {game['home_score']} - {game['away_score']} {game['away_team']}"
            send_message(TELEGRAM_CHANNEL_ID, msg)  # 推送到频道
            send_message(TELEGRAM_GROUP_ID, msg)    # 推送到群组

    # 4. 更新 KV
    redis_set("scoreboard", json.dumps(games), ex=300)  # 缓存5分钟

    return {"status": "ok", "games": len(games)}