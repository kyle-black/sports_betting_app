import redis
import os
from urllib.parse import urlparse
import json

url = os.getenv('REDIS_URL')

def tester_():
    redis_url = os.getenv('REDIS_URL')
    parsed_url = urlparse(redis_url)
    redis_client = redis.Redis(host=parsed_url.hostname, port=parsed_url.port, password=parsed_url.password)

    redis_key = 'run_stats'

    redis_data_raw = redis_client.get(redis_key)

    redis_data = json.loads(redis_data_raw.decode('utf-8'))

    return redis_data
    #print(redis_data)



if __name__ in "__main__":
    print(tester_())