import requests
import json
import redis
import os


def fetch_and_store_data(redis_client):
    url = "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/?regions=us&markets=h2h&oddsFormat=american&apiKey=c47c3bdfd870b70a41d35c839dcab514"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Error fetching data. Status code:", response.status_code)
        return

    data = response.json()

    if not data:
        print("No data fetched.")
        return

    print("Fetched data:", data)

    # Store the data in Redis with an expiration time (e.g., 5 minutes)
    try:
        redis_client.delete('mlb_data')
    except:
        redis_client.set("mlb_data", json.dumps(data))

    url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?regions=us&markets=h2h&oddsFormat=american&apiKey=7a29fdc77828ef42a5c65e00dffc586f"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Error fetching data. Status code:", response.status_code)
        return

    data = response.json()

    if not data:
        print("No data fetched.")
        return

    #print("Fetched data:", data)

    # Store the data in Redis with an expiration time (e.g., 5 minutes)
    
    redis_client.set("nba_data", json.dumps(data))


    url = "https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds/?regions=us&markets=h2h&oddsFormat=american&apiKey=7a29fdc77828ef42a5c65e00dffc586f"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Error fetching data. Status code:", response.status_code)
        return

    data = response.json()

    if not data:
        print("No data fetched.")
        return

   # print("Fetched data:", data)

    # Store the data in Redis with an expiration time (e.g., 5 minutes)
    redis_client.set("nhl_data", json.dumps(data))



    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    print("Data stored in Redis.")


#print(fetch_and_store_data())
    


#print(fetch_and_store_data())
if __name__ in "__main__":
    REDIS_KEY = "mlb_data"

    REDIS_HOST = os.getenv('REDIS_URL')
    redis_client = redis.Redis(host=REDIS_HOST)
    
    print(fetch_and_store_data(redis_client))
    #redis_data = redis_client.get(REDIS_KEY)
   # data = json.loads(redis_data)

   # print(data)