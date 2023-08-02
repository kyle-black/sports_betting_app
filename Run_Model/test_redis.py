import redis
import os
from urllib.parse import urlparse
import json

url = os.getenv('REDIS_URL')


redis_url = os.getenv('REDIS_URL')
parsed_url = urlparse(redis_url)
redis_client = redis.Redis(host=parsed_url.hostname, port=parsed_url.port, password=parsed_url.password)

redis_key = 'mlb_data'

redis_data_raw = redis_client.get(redis_key)

redis_data = json.loads(redis_data_raw.decode('utf-8'))


print(redis_data)
