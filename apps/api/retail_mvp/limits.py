"""Anonymous quota controls. Redis is required on Vercel; local state is development-only."""
from collections import defaultdict
import hashlib
import hmac
import time
import httpx
from .config import Settings

class LimitError(Exception):
    def __init__(self, code: str, retry_after: int = 60, status: int = 429):
        self.code, self.retry_after, self.status = code, retry_after, status

COUNTS: dict[str, int] = defaultdict(int)
LUA = '''
for i=1,#KEYS do
  if tonumber(redis.call('GET',KEYS[i]) or '0') + tonumber(ARGV[(i-1)*3+1]) > tonumber(ARGV[(i-1)*3+2]) then return i end
end
for i=1,#KEYS do
  local delta=tonumber(ARGV[(i-1)*3+1])
  if delta>0 then redis.call('INCRBY',KEYS[i],delta); redis.call('EXPIRE',KEYS[i],tonumber(ARGV[(i-1)*3+3])) end
end
return 0
'''

def shared_configured(s: Settings) -> bool:
    return s.redis_url.startswith('https://') and bool(s.redis_token and len(s.salt) >= 24)

async def enforce(identity: str, s: Settings, tokens: int = 0, request: bool = True) -> None:
    minute, day = int(time.time()) // 60, int(time.time()) // 86400
    digest = hmac.new((s.salt or 'local-development-only').encode(), identity.encode(), hashlib.sha256).hexdigest()[:32]
    keys = [f'ra:r:{minute}:{digest}', f'ra:global:{day}', f'ra:t:{day}', f'ra:tm:{minute}']
    deltas = [int(request), int(request), tokens, tokens]
    caps = [s.rpm, s.daily, s.tokens_daily, s.tokens_minute]
    if shared_configured(s):
        arguments = []
        for delta, cap, ttl in zip(deltas, caps, [120, 172800, 172800, 120]):
            arguments.extend([str(delta), str(cap), str(ttl)])
        try:
            async with httpx.AsyncClient(timeout=3) as client:
                response = await client.post(s.redis_url, headers={'Authorization': 'Bearer ' + s.redis_token}, json=['EVAL', LUA, '4', *keys, *arguments])
                response.raise_for_status()
                payload = response.json()
                if payload.get('error') or 'result' not in payload:
                    raise ValueError('Invalid limiter response')
                rejected = int(payload['result'])
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            raise LimitError('rate_limit_unavailable', 30, 503) from None
    elif s.require_shared:
        raise LimitError('shared_limiter_not_configured', 60, 503)
    else:
        if len(COUNTS) > 10000:
            COUNTS.clear()
        rejected = next((i + 1 for i, (key, delta, cap) in enumerate(zip(keys, deltas, caps)) if COUNTS[key] + delta > cap), 0)
        if not rejected:
            for key, delta in zip(keys, deltas):
                COUNTS[key] += delta
    if rejected:
        code = 'request_limit' if rejected == 1 else 'daily_quota' if rejected in {2, 3} else 'token_rate_limit'
        raise LimitError(code, 60 if rejected in {1, 4} else 3600)
