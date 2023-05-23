import json
import pandas as pd
import pickle
import numpy as np
import redis
#from flask import current_app
from data_fetcher import fetch_and_store_data
from apscheduler.schedulers.blocking import BlockingScheduler
import os

REDIS_HOST = os.getenv('REDIS_URL')
#REDIS_HOST = "127.0.0.1"  # Replace with your Redis server's IP address or hostname
#REDIS_PORT = 6379  # Replace with your Redis server's port
#redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
redis_client = redis.Redis(host=REDIS_HOST)

REDIS_KEY = "mlb_data"  # Replace with the actual key for the MLB data in Redis




def main():
    print(REDIS_HOST)

if __name__ in "__main__":
    #scheduler = BlockingScheduler()
    #scheduler.add_job(main, 'interval', minutes=5)
    #scheduler.start()
    main()