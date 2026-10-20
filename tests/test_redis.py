import concurrent.futures
import os
from pathlib import Path
import sys
import unittest
from uuid import uuid4
import redis

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'examples'))
from reserve import reserve


class RedisSemantics(unittest.TestCase):
    def setUp(self):
        self.client = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0'), decode_responses=True)
        self.client.ping()
        self.prefix = 'test:{' + uuid4().hex + '}:'
        self.stock = self.prefix + 'stock'
        self.client.set(self.stock, 10)

    def tearDown(self):
        keys = list(self.client.scan_iter(match=self.prefix + '*'))
        if keys:
            self.client.delete(*keys)

    def request(self, name, quantity, ttl=60):
        return reserve(self.client, self.stock, self.prefix + 'request:' + name, quantity, ttl)

    def test_retry_and_conflict(self):
        self.assertEqual(self.request('a', 3), [1, 7])
        self.assertEqual(self.request('a', 3), [1, 7])
        with self.assertRaisesRegex(redis.ResponseError, 'request conflict'):
            self.request('a', 4)
        self.assertEqual(self.client.get(self.stock), '7')
        self.assertGreater(self.client.ttl(self.prefix + 'request:a'), 0)

    def test_decline_is_stable(self):
        self.assertEqual(self.request('b', 11), [0, 10])
        self.client.set(self.stock, 20)
        self.assertEqual(self.request('b', 11), [0, 10])
        self.assertEqual(self.client.get(self.stock), '20')

    def test_invalid_arguments_do_not_write(self):
        for quantity, ttl in [(0, 60), (-1, 60), (1.5, 60), (1000000001, 60), (1, 0), (1, 604801)]:
            with self.subTest(quantity=quantity, ttl=ttl):
                with self.assertRaises(redis.ResponseError):
                    self.request('invalid', quantity, ttl)
                self.assertEqual(self.client.get(self.stock), '10')
                self.assertFalse(self.client.exists(self.prefix + 'request:invalid'))

    def test_invalid_key_type_does_not_deduct(self):
        self.client.hset(self.prefix + 'request:bad', 'x', 'y')
        with self.assertRaisesRegex(redis.ResponseError, 'invalid key type'):
            self.request('bad', 1)
        self.assertEqual(self.client.get(self.stock), '10')

    def test_concurrent_deduction_never_negative(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            results = list(pool.map(lambda n: self.request(str(n), 1), range(60)))
        self.assertEqual(sum(result[0] for result in results), 10)
        self.assertEqual(self.client.get(self.stock), '0')

    def test_concurrent_same_request_deducts_once(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            results = list(pool.map(lambda _: self.request('same', 3), range(30)))
        self.assertEqual(results, [[1, 7]] * 30)
        self.assertEqual(self.client.get(self.stock), '7')

    def test_ttl_overwrite_semantics(self):
        self.client.expire(self.stock, 60)
        self.client.incr(self.stock)
        self.assertGreater(self.client.ttl(self.stock), 0)
        self.client.set(self.stock, 12, keepttl=True)
        self.assertGreater(self.client.ttl(self.stock), 0)
        self.client.set(self.stock, 13)
        self.assertEqual(self.client.ttl(self.stock), -1)

    def test_transaction_runtime_error_does_not_rollback(self):
        self.client.set(self.stock, 'text')
        with self.client.pipeline(transaction=True) as pipe:
            pipe.incr(self.stock)
            pipe.set(self.prefix + 'ok', 'yes')
            result = pipe.execute(raise_on_error=False)
        self.assertIsInstance(result[0], redis.ResponseError)
        self.assertEqual(self.client.get(self.prefix + 'ok'), 'yes')

    def test_fixed_window(self):
        script = (Path(__file__).resolve().parents[1] / 'examples/fixed_window.lua').read_text()
        key = self.prefix + 'limit'
        self.assertEqual(self.client.eval(script, 1, key, 60), 1)
        self.assertEqual(self.client.eval(script, 1, key, 60), 2)
        self.assertGreater(self.client.ttl(key), 0)
        with self.assertRaises(redis.ResponseError):
            self.client.eval(script, 1, key, 0)
        self.assertEqual(self.client.get(key), '2')

    def test_fixed_window_invalid_ttl_does_not_write(self):
        script = (Path(__file__).resolve().parents[1] / 'examples/fixed_window.lua').read_text()
        for ttl in ['100000000000000000000', '604801', '1.5', '0', '-1']:
            key = self.prefix + 'invalid-limit:' + ttl
            with self.subTest(ttl=ttl):
                with self.assertRaises(redis.ResponseError):
                    self.client.eval(script, 1, key, ttl)
                self.assertFalse(self.client.exists(key))


if __name__ == '__main__':
    unittest.main()
