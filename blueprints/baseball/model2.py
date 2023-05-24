import json
import pandas as pd
import pickle
import numpy as np
import redis
#from flask import current_app
from data_fetcher import fetch_and_store_data
from apscheduler.schedulers.blocking import BlockingScheduler
import os
from urllib.parse import urlparse


#REDIS_HOST = "127.0.0.1"  # Replace with your Redis server's IP address or hostname
#REDIS_PORT = 6379  # Replace with your Redis server's port
REDIS_HOST = os.getenv('REDIS_URL')
REDIS_PORT = os.getenv('REDIS_PORT')

parsed_url = urlparse.urlparse(REDIS_HOST)

redis_client = redis.Redis(host=parsed_url.hostname, port=parsed_url.port)




#redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

REDIS_KEY = "mlb_data"  # Replace with the actual key for the MLB data in Redis

# Get the data from Redis
#redis_data = redis_client.get(REDIS_KEY)



#data = json.loads(redis_data)
#print(data)






def preprocess_redis_data(redis_data):
    # Load the data as a JSON object
   

    # Extract and reformat data into a list of dictionaries
    extracted_data = []
    for game in redis_data:
        row = {
            'game_id': game['id'],
            'home_team': game['home_team'],
            'away_team': game['away_team'],
            'commence_time': game['commence_time'],
            'game_date': None,  # This needs to be generated from 'commence_time' or provided separately
            'season': None,  # This information is not provided in the sample data and needs to be added
            'game_type': None  # This information is not provided in the sample data and needs to be added
        }
        for bookmaker in game['bookmakers']:
            bookmaker_key = bookmaker['key']
            for market in bookmaker['markets']:
                if market['key'] == 'h2h':
                    for outcome in market['outcomes']:
                        if outcome['name'] == row['home_team']:
                            row[f'{bookmaker_key}_home'] = outcome['price']
                        elif outcome['name'] == row['away_team']:
                            row[f'{bookmaker_key}_away'] = outcome['price']

        extracted_data.append(row)
    df = pd.DataFrame(extracted_data)
    for idx, row in df.iterrows():
        home_columns = [col for col in df.columns if col.endswith('_home')]
        away_columns = [col for col in df.columns if col.endswith('_away')]

        home_median = np.nanmedian(row[home_columns])
        away_median = np.nanmedian(row[away_columns])

        df.loc[idx, home_columns] = row[home_columns].fillna(home_median)
        df.loc[idx, away_columns] = row[away_columns].fillna(away_median)

    required_columns = ['lowvig_home', 'lowvig_away', 'betonlineag_home', 'betonlineag_away',
       'unibet_home', 'unibet_away', 'draftkings_home', 'draftkings_away',
       'pointsbetus_home', 'pointsbetus_away', 'gtbets_home', 'gtbets_away',
       'mybookieag_home', 'mybookieag_away', 'bovada_home', 'bovada_away',
       'fanduel_home', 'fanduel_away', 'intertops_home', 'intertops_away',
       'williamhill_us_home', 'williamhill_us_away', 'betrivers_home',
       'betrivers_away', 'betmgm_home', 'betmgm_away', 'sugarhouse_home',
       'sugarhouse_away', 'foxbet_home', 'foxbet_away', 'barstool_home',
       'barstool_away', 'twinspires_home', 'twinspires_away', 'betus_home',
       'betus_away', 'wynnbet_home', 'wynnbet_away', 'circasports_home',
       'circasports_away', 'superbook_home', 'superbook_away',
       'unibet_us_home', 'unibet_us_away']

    for col in required_columns:
        if col not in df.columns:
            df[col] = np.nan
    
    # Fill in missing values in each row with the median of the row
    
    # Fill in missing values in each row with the median of the row
    #df = df.apply(lambda x: x[].fillna(x.median()), axis=1)
    home_columns = [col for col in required_columns if col.endswith('_home')]
    away_columns = [col for col in required_columns if col.endswith('_away')]
    df[home_columns] = df[home_columns].apply(lambda x: x.fillna(x.median()), axis=1)
    df[away_columns] = df[away_columns].apply(lambda x: x.fillna(x.median()), axis=1)


    
    return df

    


  


def make_predictions(redis_df):
    # Load PCA and trained model
    with open('pca.pkl', 'rb') as f:
        pca = pickle.load(f)
    with open('trained_model.pkl', 'rb') as f:
        model = pickle.load(f)

    # Filter columns for X_redis
    X_redis = redis_df.loc[:, redis_df.columns.str.endswith('_home') | redis_df.columns.str.endswith('_away')]


    X_redis = X_redis[['lowvig_home', 'lowvig_away', 'betonlineag_home', 'betonlineag_away',
       'unibet_home', 'unibet_away', 'draftkings_home', 'draftkings_away',
       'pointsbetus_home', 'pointsbetus_away', 'gtbets_home', 'gtbets_away',
       'mybookieag_home', 'mybookieag_away', 'bovada_home', 'bovada_away',
       'fanduel_home', 'fanduel_away', 'intertops_home', 'intertops_away',
       'williamhill_us_home', 'williamhill_us_away', 'betrivers_home',
       'betrivers_away', 'betmgm_home', 'betmgm_away', 'sugarhouse_home',
       'sugarhouse_away', 'foxbet_home', 'foxbet_away', 'barstool_home',
       'barstool_away', 'twinspires_home', 'twinspires_away', 'betus_home',
       'betus_away', 'wynnbet_home', 'wynnbet_away', 'circasports_home',
       'circasports_away', 'superbook_home', 'superbook_away',
       'unibet_us_home', 'unibet_us_away']]
    # Scale the data
    #scaler = StandardScaler()
    

    # Apply PCA

    #print(X_redis.isnull().sum())
    X_redis_reduced = pca.transform(X_redis)

    # Make predictions
    predictions = model.predict_proba(X_redis_reduced)


     
    return predictions
    


# Preprocess the Redis data


    
def main():
    #print(fetch_and_store_data(redis_client))
    redis_data = redis_client.get(REDIS_KEY)
    #print(redis_data)
    
    redis_data = redis_client.get(REDIS_KEY)
    data = json.loads(redis_data)

    
    
    redis_df = preprocess_redis_data(data)
    #print(redis_df)


    predictions =make_predictions(redis_df)

   

    team_probabilities = {}
    for idx, row in enumerate(data):
        i_d = row['id']
        away_team = row['away_team']
        home_team = row['home_team']
        away_prob = predictions[idx][0]
        home_prob = predictions[idx][1]
        team_probabilities[i_d] = {'away_team': away_team,
                                'home_team': home_team,
                                'probs': [away_prob.item(), home_prob.item()]}

    print(team_probabilities)

    redis_client.set("mlb_predictions", json.dumps(team_probabilities))
    

if __name__ in "__main__":
    #scheduler = BlockingScheduler()
    #scheduler.add_job(main, 'interval', minutes=5)
    #scheduler.start()
    main()
