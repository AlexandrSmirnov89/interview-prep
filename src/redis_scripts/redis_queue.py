import redis
import json


class RedisQueue:
    def __init__(self, name: str = 'queue', host: str = 'localhost', port: int = 6379, db: int = 0):
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.queue_name = name

    def publish(self, msg: dict):
        self.redis_client.lpush(self.queue_name, json.dumps(msg))

    def consume(self) -> dict:
        msg = self.redis_client.rpop(self.queue_name)
        return json.loads(msg) if msg else None


if __name__ == '__main__':
    q = RedisQueue()

    q.publish({'a': 1})
    q.publish({'b': 2})
    q.publish({'c': 3})

    assert q.consume() == {'a': 1}
    assert q.consume() == {'b': 2}
    assert q.consume() == {'c': 3}