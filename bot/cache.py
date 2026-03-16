import requests
import time

CACHE = {}
CACHE_TTL = 900  # 15 minutos

def cached_request(key, url):
    now = time.time()
    if key in CACHE:
        data, timestamp = CACHE[key]
        if now - timestamp < CACHE_TTL:
            return data
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        CACHE[key] = (data, now)
        return data
    return None