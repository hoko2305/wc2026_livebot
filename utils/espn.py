import requests
import os
from utils.kv import redis_get, redis_set

ESPN_SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard"
# 若世界杯代码不对，请自行替换为正确 league

def fetch_scoreboard():
    try:
        resp = requests.get(ESPN_SCOREBOARD_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return parse_scoreboard(data)
    except Exception as e:
        print("ESPN fetch error:", e)
        return None

def parse_scoreboard(data):
    # 与之前类似，提取比赛列表
    games = []
    if 'events' in data:
        for event in data['events']:
            # ... 解析逻辑，返回结构化数据
            games.append(game)
    return games