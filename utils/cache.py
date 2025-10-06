import os, json, time, threading, httpx
_cache, _lock = {}, threading.Lock()
UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL", "")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN", "")

def cache_get(k):
    if UPSTASH_URL and UPSTASH_TOKEN:
        try:
            r = httpx.get(f"{UPSTASH_URL}/get/{k}", headers={"Authorization": f"Bearer {UPSTASH_TOKEN}"}, timeout=2)
            d = r.json().get("result")
            if d: return json.loads(d)
        except Exception: pass
    with _lock:
        v = _cache.get(k)
        if not v: return None
        val, exp = v
        if exp and time.time() > exp: _cache.pop(k, None); return None
        return val

def cache_set(k, v, ttl=600):
    if UPSTASH_URL and UPSTASH_TOKEN:
        try:
            p = json.dumps(v)
            httpx.post(f"{UPSTASH_URL}/set/{k}", headers={"Authorization": f"Bearer {UPSTASH_TOKEN}"}, content=p, timeout=2)
            httpx.post(f"{UPSTASH_URL}/expire/{k}/{ttl}", headers={"Authorization": f"Bearer {UPSTASH_TOKEN}"}, timeout=2)
            return
        except Exception: pass
    with _lock: _cache[k] = (v, time.time()+ttl)
