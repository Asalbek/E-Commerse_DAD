"""
Token-Bucket Rate Limiter — From-Scratch Implementation (R11)

Based on the token-bucket algorithm as described in
"System Design Interview" by Alex Xu (Chapter 4).

How it works:
  1. Each client (identified by key, e.g. user_id or IP) has a bucket.
  2. The bucket holds up to `capacity` tokens.
  3. Tokens are added at a fixed `refill_rate` (tokens per second).
  4. Each request consumes one token.
  5. If the bucket is empty, the request is rejected (HTTP 429).

State is stored in Redis for distributed consistency across
multiple backend replicas behind the Nginx load balancer.

Trade-offs:
  - Allows short bursts (up to `capacity`) while enforcing avg rate.
  - Distributed via Redis: works across replicas.
  - Atomic via Lua script: no race conditions.
  - Limitation: Redis latency adds ~0.5ms per request.
"""

import time
from typing import Tuple

# Lua script for atomic token bucket operation in Redis.
# KEYS[1] = bucket key
# ARGV[1] = capacity
# ARGV[2] = refill_rate (tokens per second)
# ARGV[3] = current timestamp (seconds, float)
# Returns: {allowed (0 or 1), remaining_tokens}
TOKEN_BUCKET_LUA = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens = tonumber(bucket[1])
local last_refill = tonumber(bucket[2])

if tokens == nil then
    tokens = capacity
    last_refill = now
end

-- Calculate tokens to add since last refill
local elapsed = math.max(0, now - last_refill)
local new_tokens = elapsed * refill_rate
tokens = math.min(capacity, tokens + new_tokens)

local allowed = 0
if tokens >= 1 then
    tokens = tokens - 1
    allowed = 1
end

redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
redis.call('EXPIRE', key, math.ceil(capacity / refill_rate) + 1)

return {allowed, math.floor(tokens)}
"""


class TokenBucketRateLimiter:
    """Distributed token-bucket rate limiter backed by Redis.

    Parameters:
        redis_client: an async Redis connection
        capacity: max tokens in the bucket (burst size)
        refill_rate: tokens added per second
        key_prefix: Redis key namespace
    """

    def __init__(
        self,
        redis_client,
        capacity: int = 100,
        refill_rate: float = 10.0,
        key_prefix: str = "ratelimit",
    ):
        self.redis = redis_client
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.key_prefix = key_prefix
        self._script = None

    async def _get_script(self):
        if self._script is None:
            self._script = self.redis.register_script(TOKEN_BUCKET_LUA)
        return self._script

    async def allow_request(self, client_key: str) -> Tuple[bool, int]:
        """Check whether a request from `client_key` is allowed.

        Returns:
            (allowed: bool, remaining_tokens: int)
        """
        script = await self._get_script()
        bucket_key = f"{self.key_prefix}:{client_key}"
        now = time.time()

        result = await script(
            keys=[bucket_key],
            args=[self.capacity, self.refill_rate, now],
        )

        allowed = bool(result[0])
        remaining = int(result[1])
        return allowed, remaining

    async def reset(self, client_key: str):
        """Reset a client's bucket (e.g. after ban lift)."""
        bucket_key = f"{self.key_prefix}:{client_key}"
        await self.redis.delete(bucket_key)
