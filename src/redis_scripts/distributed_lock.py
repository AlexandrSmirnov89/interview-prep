import time

import redis
import datetime
import functools

redis_client = redis.Redis(host='localhost', port=6379, db=0)


def single(max_processing_time: datetime.timedelta):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            lock_key = f'lock:{func.__name__}'
            lock = redis_client.set(lock_key, 'locked', ex=int(max_processing_time.total_seconds()), nx=True)
            if not lock:
                return
            try:
                return func(*args, **kwargs)
            finally:
                redis_client.delete(lock_key)

        return wrapper
    return decorator

@single(max_processing_time=datetime.timedelta(minutes=2))
def process_transaction():
    time.sleep(2)
