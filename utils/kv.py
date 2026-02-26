import os
import requests
import json

REDIS_URL = os.getenv("REDIS_URL")
REDIS_TOKEN = os.getenv("REDIS_TOKEN")

headers = {
    "Authorization": f"Bearer {REDIS_TOKEN}",
    "Content-Type": "application/json"
}

def redis_get(key):
    resp = requests.get(f"{REDIS_URL}/get/{key}", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        return data.get("result")
    return None

def redis_set(key, value, ex=None):
    payload = {
        "key": key,
        "value": value
    }
    if ex:
        payload["ex"] = ex
    resp = requests.post(f"{REDIS_URL}/set", json=payload, headers=headers)
    return resp.status_code == 200