"""单商品幂等预留。仅 --reset 清理演示专用命名空间。"""
import argparse
import os
from pathlib import Path
import redis

SCRIPT = Path(__file__).with_suffix('.lua').read_text(encoding='utf-8')


def reserve(client, stock_key, request_key, quantity, ttl=86400):
    return client.eval(SCRIPT, 2, stock_key, request_key, quantity, ttl)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()
    client = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0'), decode_responses=True)
    prefix = 'book:{sku:demo}:'
    if args.reset:
        for key in client.scan_iter(match=prefix + '*', count=100):
            client.delete(key)
        client.set(prefix + 'stock', 10)
    if not client.exists(prefix + 'stock'):
        parser.error('请先运行 --reset 初始化独立示例库存')
    for request_id, quantity in [('a', 3), ('a', 3), ('b', 8), ('a', 4)]:
        try:
            result = reserve(client, prefix + 'stock', prefix + 'request:' + request_id, quantity)
            print(f'request={request_id} quantity={quantity} result={result}')
        except redis.ResponseError as exc:
            print(f'request={request_id} error={exc}')
    print('stock=', client.get(prefix + 'stock'))


if __name__ == '__main__':
    main()
