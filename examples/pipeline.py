"""有界批量写入与读取；不使用 MULTI/EXEC。"""
import os
from uuid import uuid4
import redis

client = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0'), decode_responses=True)
keys = [f'lab:pipeline:{uuid4().hex}:{i}' for i in range(100)]
try:
    with client.pipeline(transaction=False) as pipe:
        for i, key in enumerate(keys):
            pipe.set(key, i, ex=60)
        assert all(pipe.execute())
    assert client.mget(keys) == [str(i) for i in range(100)]
    print('100 次有界写入与读取通过')
finally:
    client.delete(*keys)
