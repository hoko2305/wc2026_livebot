from http.server import BaseHTTPRequestHandler
import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.telegram import send_message
from utils.deepseek import predict_match

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        update = json.loads(post_data)

        # 处理消息
        if 'message' in update:
            chat_id = update['message']['chat']['id']
            text = update['message'].get('text', '')

            if text.startswith('/predict'):
                # 格式: /predict 球队A 球队B
                parts = text.split()
                if len(parts) >= 3:
                    team1 = parts[1]
                    team2 = parts[2]
                    prediction = predict_match(team1, team2)
                    send_message(chat_id, f"🤖 预测结果：\n{prediction}")
                else:
                    send_message(chat_id, "请使用格式：/predict 球队A 球队B")

            elif text == '/live':
                # 从 KV 获取比分
                from utils.kv import redis_get
                scoreboard_json = redis_get("scoreboard")
                if scoreboard_json:
                    import json
                    games = json.loads(scoreboard_json)
                    msg = "\n".join([f"{g['home_team']} {g['home_score']} - {g['away_score']} {g['away_team']}" for g in games])
                    send_message(chat_id, f"实时比分：\n{msg}")
                else:
                    send_message(chat_id, "暂无比赛数据")

            elif text == '/start':
                send_message(chat_id, "欢迎使用世界杯机器人！\n可用命令：\n/live\n/predict 球队A 球队B")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")