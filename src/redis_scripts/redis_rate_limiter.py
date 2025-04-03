import redis
import time
import random


class RateLimitExceed(Exception):
    pass


class RateLimiter:
    def __init__(self, key: str, max_requests: int = 5, window: int = 3):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.key = f'rate_limit:{key}'
        self.max_requests = max_requests
        self.window = window

    def test(self) -> bool:
        now = time.time()
        pipeline = self.redis.pipeline(transaction=True)

        pipeline.lpush(self.key, now)
        pipeline.ltrim(self.key, 0, self.max_requests - 1)
        pipeline.expire(self.key, self.window)
        pipeline.execute()

        request_count = self.redis.llen(self.key)
        return request_count <= self.max_requests


def make_api_request(rate_limiter: RateLimiter):
    if not rate_limiter.test():
        raise RateLimitExceed
    else:
        pass


if __name__ == '__main__':
    rate_limiter = RateLimiter(key='api_request')

    for _ in range(50):
        time.sleep(random.uniform(0.5, 1.5))

        try:
            make_api_request(rate_limiter)
        except RateLimitExceed:
            print('Rate limit exceeded!')
        else:
            print('All good')
