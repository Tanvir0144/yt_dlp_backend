import time, threading
from collections import defaultdict
from dataclasses import dataclass

@dataclass
class RateLimitConfig:
    capacity:int=60; refill_rate:float=1.0; burst:int=20

_buckets=defaultdict(lambda:{"tokens":0.0,"ts":0.0}); _lock=threading.Lock()

def rate_limit_ok(ip,key,cfg):
    now=time.time();bid=f"{ip}:{key}"
    with _lock:
        b=_buckets[bid];elapsed=now-b["ts"];ref=elapsed*cfg.refill_rate
        b["tokens"]=min(cfg.capacity+cfg.burst,b["tokens"]+ref);b["ts"]=now
        if b["tokens"]>=1.0: b["tokens"]-=1.0;return True
        return False
