
import pandas as pd
import redis
import json
import numpy as np
import pickle
import os
from urllib.parse import urlparse
from datetime import datetime
import schedule
import time



#####REDIS CONNECTION
REDIS_HOST = os.getenv('REDIS_URL')
parsed_url = urlparse(REDIS_HOST)
redis_client = redis.Redis(host=parsed_url.hostname, port=parsed_url.port, password=parsed_url.password)
REDIS_KEY = "mlb_data" 
###############################
####### MLB STAT CONNECTION

stats =pd.read_csv('model/stats/2023_team.csv')
######################################

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
        has_lowvig =False
        for bookmaker in game['bookmakers']:
            bookmaker_key = bookmaker['key']
            if bookmaker_key =='lowvig':
                has_lowvig=True
            for market in bookmaker['markets']:
                if market['key'] == 'h2h':
                    for outcome in market['outcomes']:
                        if outcome['name'] == row['home_team']:
                            row[f'{bookmaker_key}_home'] = outcome['price']
                        elif outcome['name'] == row['away_team']:
                            row[f'{bookmaker_key}_away'] = outcome['price']

        if has_lowvig:
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

def american_to_implied_probability(american_odds):
    """
    Convert American odds to implied probability
    """
    if american_odds > 0:
        return 100 / (american_odds + 100)
    else:
        return abs(american_odds) / (abs(american_odds) + 100)
    

def calculate_vig(american_odds1, american_odds2):
    """
    Calculate the vig given two American odds
    """

    # Calculate the implied probabilities from the odds
    prob1 = american_to_implied_probability(american_odds1)
    prob2 = american_to_implied_probability(american_odds2)

    # The vig is the excess of these probabilities over 1
    vig = prob1 + prob2 - 1

    return vig



#sportsbooks = ['pinnacle', 'lowvig', 'betonlineag', 'draftkings', 'fanduel']


def create_dataset(redis_data,stats):
    df = pd.DataFrame()
    #stat_df = stats[['home_R','away_R','home_RA','away_RA', 'home_W-L%', 'away_W-L%','home_Luck','away_Luck','lowvig_home','lowvig_away']]
    df['home_team'] = redis_data['home_team']
    df['away_team'] = redis_data['away_team']
    df['lowvig_home'] = redis_data['lowvig_home']
    df['lowvig_away'] = redis_data['lowvig_away']
    df['game_id'] = redis_data['game_id']
    df_home=df.merge(stats,how='left', left_on='home_team', right_on='Tm')
    #return df_home
    
    df_home =df_home[['game_id','home_team','R','RA','W-L%','Luck','lowvig_home']]

    df_home.rename(columns={'R':'home_R','RA':'home_RA', 'W-L%':'home_W-L%', 'Luck':'home_Luck'}, inplace=True)
    df_home['lowvig_home_vf']=df_home.apply(lambda row: american_to_implied_probability(row['lowvig_home']), axis=1)
    
    df_away=df.merge(stats,  left_on='away_team', right_on='Tm')
    df_away =df_away[['game_id','away_team','R','RA','W-L%','Luck', 'lowvig_away']]
    df_away['lowvig_away_vf'] = df_away.apply(lambda row: american_to_implied_probability(row['lowvig_away']), axis=1)

    df_away.rename(columns={'R':'away_R','RA':'away_RA', 'W-L%':'away_W-L%', 'Luck':'away_Luck'}, inplace =True)

    df = df_home.merge(df_away, left_on='game_id', right_on='game_id')



    df =df[['game_id','home_team','away_team','home_R','away_R','home_RA','away_RA', 'home_W-L%', 'away_W-L%','home_Luck','away_Luck','lowvig_home_vf','lowvig_away_vf','lowvig_home','lowvig_away']]
    

    
    
    return df

def make_predictions(df):
    with open(f'model/trained_model/trained_model_34.pkl', 'rb') as file:
        model = pickle.load(file)

        # Remove game_id before making predictions
        game_ids = df['game_id']
        input_features = df.drop(columns=['game_id','away_team','home_team'])
        
        # Get predictions
        predictions = model.predict_proba(input_features)
        
        # Return a DataFrame including game_id and predictions
        prediction_df = pd.DataFrame(predictions, columns=['away_prob', 'home_prob'])
        prediction_df['game_id'] = game_ids.values
        return prediction_df
    

def main():
    # fetch and preprocess data
    redis_data = redis_client.get(REDIS_KEY)
    data = json.loads(redis_data)
    redis_df = preprocess_redis_data(data)

    # create input data for model and make predictions
    input_data = create_dataset(redis_df, stats)
    predictions = make_predictions(input_data)

    # merge input_data and predictions on 'game_id'
    merged_df = pd.merge(input_data, predictions, on='game_id')

    # initialize team_probabilities dict
    team_probabilities = {}

    for idx, row in merged_df.iterrows():
        game_id = row['game_id']
        away_team = row['away_team']
        home_team = row['home_team']
        away_prob = row['away_prob']
        home_prob = row['home_prob']

        team_probabilities[game_id] = {'away_team': away_team,
                                        'home_team': home_team,
                                        'probs': [away_prob, home_prob]}

    print(team_probabilities)

    # store the team_probabilities to redis
    redis_client.set("mlb_predictions", json.dumps(team_probabilities))








    




if __name__ in "__main__":
    current_time = datetime.now().time()
    print("StartTime:",current_time)
    #scheduler = BlockingScheduler()
    #scheduler.add_job(main, 'interval', minutes=5)
    #scheduler.start()
    print("Pull Time",current_time)


#    main()


    
    schedule.every(5).minutes.do(main)

    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            print(e)
        finally:
            time.sleep(5)
    