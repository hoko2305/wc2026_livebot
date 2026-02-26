# api/cron.py
from http.server import BaseHTTPRequestHandler
import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.espn import fetch_scoreboard
from utils.telegram import send_message
from utils.kv import redis_get, redis_set

TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
TELEGRAM_GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """处理 GET 请求（Vercel Cron 会通过 GET 触发）"""
        # 1. 抓取 ESPN 数据
        games = fetch_scoreboard()
        if not games:
            self._send_response(200, {"status": "no data"})
            return

        # 2. 从 KV 获取上次数据
        last_games_json = redis_get("scoreboard")
        last_games = json.loads(last_games_json) if last_games_json else []

        # 3. 检测事件（比分变化）
        for game in games:
            game_id = game['game_id']
            last_game = next((g for g in last_games if g['game_id'] == game_id), None)
            if last_game and (last_game['home_score'] != game['home_score'] or last_game['away_score'] != game['away_score']):
                msg = f"⚽ 比分更新！\n{game['home_team']} {game['home_score']} - {game['away_score']} {game['away_team']}"
                send_message(TELEGRAM_CHANNEL_ID, msg)
                send_message(TELEGRAM_GROUP_ID, msg)

        # 4. 更新缓存
        redis_set("scoreboard", json.dumps(games), ex=300)

        # 返回成功响应
        self._send_response(200, {"status": "ok", "games": len(games)})

    def _send_response(self, status_code, data):
        """辅助方法：发送 JSON 响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
