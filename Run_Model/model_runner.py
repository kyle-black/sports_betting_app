import pandas as pd
import numpy as np
import sqlite3
import pull_stats ##### Pulls team stats from webscrapping and into Redis
import odds_fetcher #### Pulls Odds from API and into Redis
from Run_Model.model import model_output

import json

import redis
import os
from urllib.parse import urlparse

class Pull_Data():

    def __init__(self):
        
        
        url =os.getenv('REDIS_URL')
        parsed_url =urlparse(url)
        self.redis_client = redis.Redis(host=parsed_url.hostname, port=parsed_url.port, password=parsed_url.password)
        
        odds_fetcher.fetch_and_store_data(self.redis_client)
        
        
        ##########Pulls Current Games, Odds and Stats from Redis
        self.runs_raw=self.redis_client.get('run_stats')
        self.opp_runs_raw= self.redis_client.get('opp_stats')
        self.win_pct_raw = self.redis_client.get('win_stats')
        self.games_raw= self.redis_client.get('mlb_data')
        ########################################################

        # convert byte string from Redis to string and then to JSON
        self.games = json.loads(self.games_raw.decode('utf-8'))
        
        self.runs = json.loads(self.runs_raw.decode('utf-8'))
        self.opp_runs = json.loads(self.opp_runs_raw.decode('utf-8'))
        self.win_pct = json.loads(self.win_pct_raw.decode('utf-8'))

        # Convert lists to pandas DataFrames
        #self.redis_data = pd.DataFrame(self.redis_data)
        
        self.games = self.preprocess_redis_data(self.games)

        self.runs = pd.DataFrame(self.runs)
        self.opp_runs = pd.DataFrame(self.opp_runs)
        self.win_pct = pd.DataFrame(self.win_pct)
        
    def preprocess_redis_data(self,df):
        # Load the data as a JSON object
        redis_data = df

        # Extract and reformat data into a list of dictionaries
        extracted_data = []
        for game in redis_data:
            row = {
                'game_id': game['id'],
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'commence_time': game['commence_time'],
                'game_date': game['commence_time'],  # This needs to be generated from 'commence_time' or provided separately
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

        required_columns = ['game_id','home_team','away_team', 'game_date','lowvig_home', 'lowvig_away', 'betonlineag_home', 'betonlineag_away',
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


        self.games=df
        
        return self.games
class Combine_Data(Pull_Data):
    def __init__(self):
        # Call parent's init method
       
        super().__init__()
        #self.home_win_pct = pd.DataFrame()
        #self.away_win_pct = pd.DataFrame()

    def normalize(self,series):
        return (series - series.min()) / (series.max() - series.min())
    

    def add_rolling_pct(self, df_,type_,days=[10, 30]):
        df_ = df_.sort_values('Date')  # Sort by date
        df_.set_index('Date', inplace=True)  # Set date as index

        for day in days:
            # Group by team and calculate rolling mean for each team
            df_[f'Rolling_{day}D_{type_}'] = df_.groupby('Team')['Current'].transform(
            lambda x: x.rolling(day).mean())

        df_.reset_index(inplace=True)  # Reset index

        return df_



 ############################### Add Win Pct ##################################       
    def win_pct_add(self):
        self.win_pct = self.win_pct[['Date','Team', 'Current','Last 3','Last 1', 'Home', 'Away', 'Previous']]
        self.win_pct = self.win_pct.replace('--', np.nan)
        self.win_pct[['Current','Last 3','Last 1', 'Home', 'Away', 'Previous']]=self.win_pct[['Current','Last 3','Last 1', 'Home', 'Away', 'Previous']].apply(pd.to_numeric)
        
        ##################ADD ROLLING PCT FUNCTION
        self.win_pct = self.add_rolling_pct(self.win_pct,'win')
        #######################################################


        
        
        self.home_win_pct = self.win_pct.copy()
        self.away_win_pct = self.win_pct.copy()
        
        self.home_win_pct.rename(columns ={'Date':'home_Date','Team':'home_Team', 'Current':'home_Current_win_pct','Rolling_10D_win':'home_Rolling_10D_win' ,'Rolling_30D_win':'home_Rolling_30D_win','Last 3':'home_3_win_pct','Last 1':'home_1_win_pct','Home':'home_Home_win_pct', 'Away': 'home_Away_win_pct', 'Previous':'home_prev_win_pct'}, inplace =True)
        for col in ['home_Current_win_pct','home_3_win_pct', 'home_1_win_pct', 'home_Home_win_pct', 'home_Away_win_pct', 'home_prev_win_pct','home_Rolling_10D_win', 'home_Rolling_30D_win']:
            self.home_win_pct[col] = self.home_win_pct.groupby('home_Date')[col].transform(self.normalize)


        ###################RENAME COLUMNS 
        '''
        self.home_win_pct.rename(columns ={'Date':'home_Date','Team':'home_Team', 'Current':'home_Current_win_pct', 'Last 3':'home_3_win_pct','Last 1':'home_1_win_pct','Home':'home_Home_win_pct', 'Away': 'home_Away_win_pct', 'Previous':'home_prev_win_pct'}, inplace =True)
        for col in ['home_Current_win_pct','home_3_win_pct', 'home_1_win_pct', 'home_Home_win_pct', 'home_Away_win_pct', 'home_prev_win_pct','Rolling_10D_win', 'Rolling_30D_win']:
            self.home_win_pct[col] = self.home_win_pct.groupby('home_Date')[col].transform(self.normalize)
        '''
        ################################################################################
        
        
        teamname = {'Arizona':'Arizona Diamondbacks','Atlanta':'Atlanta Braves', 'Baltimore':'Baltimore Orioles','Boston':'Boston Red Sox','Chi Cubs':'Chicago Cubs','Chi White Sox':'Chicago White Sox','Cincinnati':'Cincinnati Reds','Cleveland':'Cleveland Guardians','Colorado':'Colorado Rockies','Detroit':'Detroit Tigers','Houston':'Houston Astros','Kansas City':'Kansas City Royals', 'LA Angels':'Los Angeles Angels', 'LA Dodgers': 'Los Angeles Dodgers','Miami':'Miami Marlins', 'Milwaukee':'Milwaukee Brewers','Minnesota':'Minnesota Twins','NY Mets':'New York Mets', 'NY Yankees':'New York Yankees', 'Oakland':'Oakland Athletics','Philadelphia':'Philadelphia Phillies','Pittsburgh':'Pittsburgh Pirates', 'San Diego': 'San Diego Padres','San Francisco': 'San Francisco Giants', 'Seattle':'Seattle Mariners', 'St. Louis':'St.Louis Cardinals', 'Tampa Bay':'Tampa Bay Rays','Texas':'Texas Rangers', 'Toronto': 'Toronto Blue Jays','Washington':'Washington Nationals'}
        self.home_win_pct['home_Team'].replace(teamname, inplace =True)

        self.away_win_pct.rename(columns ={'Date':'away_Date','Team':'away_Team', 'Current':'away_Current_win_pct', 'Last 3':'away_3_win_pct','Last 1':'away_1_win_pct','Rolling_10D_win':'away_Rolling_10D_win' ,'Rolling_30D_win':'away_Rolling_30D_win','Home':'away_Home_win_pct', 'Away': 'away_Away_win_pct', 'Previous':'away_prev_win_pct'}, inplace=True)
        for col in ['away_Current_win_pct','away_3_win_pct', 'away_1_win_pct', 'away_Home_win_pct', 'away_Away_win_pct', 'away_prev_win_pct','away_Rolling_10D_win', 'away_Rolling_30D_win']:
            self.away_win_pct[col] = self.away_win_pct.groupby('away_Date')[col].transform(self.normalize)

        '''
        self.away_win_pct.rename(columns ={'Date':'away_Date','Team':'away_Team', 'Current':'away_Current_win_pct', 'Last 3':'away_3_win_pct','Last 1':'away_1_win_pct','Home':'away_Home_win_pct', 'Away': 'away_Away_win_pct', 'Previous':'away_prev_win_pct'}, inplace=True)
        for col in ['away_Current_win_pct','away_3_win_pct', 'away_1_win_pct', 'away_Home_win_pct', 'away_Away_win_pct', 'away_prev_win_pct','Rolling_10D_win', 'Rolling_30D_win']:
            self.away_win_pct[col] = self.away_win_pct.groupby('away_Date')[col].transform(self.normalize)
        '''
        self.away_win_pct['away_Team'].replace(teamname, inplace =True)

        return self.home_win_pct, self.away_win_pct
    
############################### Add Win Pct ##################################     
    def combine_game_win(self):
        self.home_win_pct, self.away_win_pct = self.win_pct_add()
        self.games['game_date'] = pd.to_datetime(self.games['game_date']).dt.date
        self.home_win_pct['home_Date'] = pd.to_datetime(self.home_win_pct['home_Date']).dt.date
        self.away_win_pct['away_Date'] = pd.to_datetime(self.away_win_pct['away_Date']).dt.date
        self.merged_df = self.games.merge(self.home_win_pct, how='left', left_on=['home_team', 'game_date'], right_on = ['home_Team', 'home_Date'])
        self.merged_df = self.merged_df.merge(self.away_win_pct, how='left', left_on=['away_team', 'game_date'], right_on = ['away_Team', 'away_Date'])

        return self.merged_df
    
    def find_home_cols(self,df):
            return [col for col in df if col.endswith('_home')]

    def find_away_cols(self,df):
            return [col for col in df if col.endswith('_away')]
    
    '''
    def combine_game_odds(self):
        
        self.merged_df = self.combine_game_win()
        
         
            
       # self.merged_df = self.merged_df.groupby('game_id').apply(lambda group: group.fillna(method='ffill').fillna(method='bfill'))
        #self.merged_df = self.merged_df.drop_duplicates(subset='game_id', keep='last')
        self.merged_df['game_date'] = pd.to_datetime(self.merged_df['game_date']).dt.tz_convert('US/Eastern').dt.date
        home_cols = self.find_home_cols(self.merged_df)
        away_cols = self.find_away_cols(self.merged_df)
        
        # Replace odds that are >400 or <-400 with NaN in home_odds and away_odds columns
        for col in home_cols:
            self.merged_df[col] = self.merged_df[col].where(self.merged_df[col].between(-400, 400), np.nan)
        for col in away_cols:
            self.merged_df[col] = self.merged_df[col].where(self.merged_df[col].between(-400, 400), np.nan)

        self.merged_df['home_median'] = self.merged_df[home_cols].apply(lambda row: row.median() if row.count() >= 5 else np.nan, axis=1)
        self.merged_df['away_median'] = self.merged_df[away_cols].apply(lambda row: row.median() if row.count() >= 5 else np.nan, axis=1)
        self.merged_df['home_mean'] = self.merged_df[home_cols].apply(lambda row: row.mean() if row.count() >= 5 else np.nan, axis=1)
        self.merged_df['away_mean'] = self.merged_df[away_cols].apply(lambda row: row.mean() if row.count() >= 5 else np.nan, axis=1)
        
        self.merged_df = self.merged_df.drop_duplicates(subset='game_id', keep='last')
        self.merged_df = self.merged_df.merge(self.merged_df, how='left', left_on=['home_team', 'away_team','game_date'], right_on=['home_team','away_team','game_date'])
        
        return self.merged_df
    '''
    ######################################COMBINE GAME RUNS #########################################
        ######################################COMBINE GAME RUNS #########################################
        
    def combine_game_runs(self):
        #self.merged_df =self.combine_game_odds()
        #self.runs.drop(['Unnamed: 0','Unnamed: 9'], inplace=True, axis =1)
        #self.win_pct = self.win_pct[['Date','Team', 'Current','Last 3','Last 1', 'Home', 'Away', 'Previous']]
        self.merged_df =self.combine_game_win()
        teamname ={'Arizona':'Arizona Diamondbacks','Atlanta':'Atlanta Braves', 'Baltimore':'Baltimore Orioles','Boston':'Boston Red Sox','Chi Cubs':'Chicago Cubs','Chi White Sox':'Chicago Sox','Cincinnati':'Cincinnati Reds','Cleveland':'Cleveland Guardians','Colorado':'Colorado Rockies','Detroit':'Detroit Tigers','Houston':'Houston Astros','Kansas City':'Kansas City Royals', 'LA Angels':'Los Angeles Angels', 'LA Dodgers': 'Los Angeles Dodgers','Miami':'Miami Marlins', 'Milwaukee':'Milwaukee Brewers','Minnesota':'Minnesota Twins','NY Mets':'New York Mets', 'NY Yankees':'New York Yankees', 'Oakland':'Oakland Athletics','Philadelphia':'Philadelphia Phillies','Pittsburgh':'Pittsburgh Pirates', 'San Diego': 'San Diego Padres','SF Giants': 'San Francisco Giants', 'Seattle':'Seattle Mariners', 'St. Louis':'St.Louis Cardinals', 'Tampa Bay':'Tampa Bay Rays','Texas':'Texas Rangers', 'Toronto': 'Toronto Blue Jays','Washington':'Washington Nationals'}
        self.runs['Team'].replace(teamname, inplace =True)
        self.runs = self.runs.replace('--', np.nan)
        self.runs[['Current','Last 3','Last 1', 'Home', 'Away', 'Previous']]=self.win_pct[['Current','Last 3','Last 1', 'Home', 'Away', 'Previous']].apply(pd.to_numeric)
        
        ##################ADD ROLLING PCT FUNCTION
        self.runs = self.add_rolling_pct(self.runs,'runs')
        #######################################################
        self.home_runs = self.runs.copy()
        self.away_runs = self.runs.copy()
        ######################################################
        ###################RENAME COLUMNS 
        self.home_runs.rename(columns ={'Date':'home_Date','Team':'home_Team', 'Current':'home_r_Current', 'Last 3':'home_r_3','Last 1':'home_r_1','Home':'home_r_Home', 'Away': 'home_r_Away', 'Previous':'home_r_prev','Rolling_10D_runs':'Rolling_10D_r_home','Rolling_30D_runs':'Rolling_30D_r_home'}, inplace =True)
        for col in ['home_r_Current','home_r_3', 'home_r_1', 'home_r_Home', 'home_r_Away', 'home_r_prev','Rolling_10D_r_home', 'Rolling_30D_r_home']:
            self.home_runs[col] = self.home_runs.groupby('home_Date')[col].transform(self.normalize)
        ################################################################################

         ###################RENAME COLUMNS 
        self.away_runs.rename(columns ={'Date':'away_Date','Team':'away_Team', 'Current':'away_r_Current', 'Last 3':'away_r_3','Last 1':'away_r_1','Home':'away_r_Home', 'Away': 'away_r_Away', 'Previous':'away_r_prev','Rolling_10D_runs':'Rolling_10D_r_away','Rolling_30D_runs':'Rolling_30D_r_away'}, inplace =True)
        #self.away_runs.rename(columns ={'Date':'away_Date','Team':'away_Team', 'Current':'away_r_Current', 'Last 3':'away_r_3','Last 1':'away_r_1','Home':'away_r_Home', 'Away': 'away_r_Away', 'Previous':'away_r_prev'}, inplace =True)
        #return self.away_runs
        
        for col in ['away_r_Current','away_r_3', 'away_r_1', 'away_r_Home', 'away_r_Away', 'away_r_prev','Rolling_10D_r_away', 'Rolling_30D_r_away']:
            self.away_runs[col] = self.away_runs.groupby('away_Date')[col].transform(self.normalize)
        ################################################################################
        
        self.home_runs['home_r_Date'] = pd.to_datetime(self.home_runs['home_Date'], errors='coerce').dt.date
        self.away_runs['away_r_Date'] = pd.to_datetime(self.away_runs['away_Date'], errors='coerce').dt.date

        self.merged_df=self.merged_df.merge(self.home_runs, how='left', left_on=['home_team','game_date'], right_on=['home_Team','home_r_Date'])
        self.merged_df=self.merged_df.merge(self.away_runs, how='left', left_on=['away_team','game_date'], right_on=['away_Team','away_r_Date'])

        self.merged_df= self.merged_df[['game_id', 'home_team', 'away_team', 'commence_time',
       'game_date', 'draftkings_home',
       'draftkings_away', 'pointsbetus_home', 'pointsbetus_away',
       'williamhill_us_home', 'williamhill_us_away', 'betus_home',
       'betus_away', 'mybookieag_home', 'mybookieag_away', 'barstool_home',
       'barstool_away', 'betmgm_home', 'betmgm_away', 'fanduel_home',
       'fanduel_away', 'lowvig_home', 'lowvig_away', 'betonlineag_home',
       'betonlineag_away', 'superbook_home', 'superbook_away', 'wynnbet_home',
       'wynnbet_away', 'bovada_home', 'bovada_away', 'betrivers_home',
       'betrivers_away', 'twinspires_home', 'twinspires_away',
       'unibet_us_home', 'unibet_us_away', 'unibet_home', 'unibet_away',
       'gtbets_home', 'gtbets_away', 'intertops_home', 'intertops_away',
       'sugarhouse_home', 'sugarhouse_away', 'foxbet_home', 'foxbet_away',
       'circasports_home', 'circasports_away', 'home_Current_win_pct', 'home_3_win_pct', 'home_1_win_pct',
       'home_Home_win_pct', 'home_Away_win_pct', 'home_prev_win_pct',
       'home_Rolling_10D_win', 'home_Rolling_30D_win','away_Current_win_pct', 'away_3_win_pct',
       'away_1_win_pct', 'away_Home_win_pct', 'away_Away_win_pct',
       'away_prev_win_pct', 'away_Rolling_10D_win', 'away_Rolling_30D_win','home_r_Current', 'home_r_3', 'home_r_1',
       'home_r_Home', 'home_r_Away', 'home_r_prev', 'Rolling_10D_r_home',
       'Rolling_30D_r_home','away_r_Current', 'away_r_3', 'away_r_1', 'away_r_Home', 'away_r_Away',
       'away_r_prev', 'Rolling_10D_r_away', 'Rolling_30D_r_away']]
       
        return self.merged_df
       
######################################COMBINE GAME OPP RUNS #########################################
    
    def combine_game_runs_opp(self):
            self.merged_df =self.combine_game_runs()
           # self.runs.drop(['Unnamed: 0','Unnamed: 9'], inplace=True, axis =1)
            #self.win_pct = self.win_pct[['Date','Team', 'Current','Last 3','Last 1', 'Home', 'Away', 'Previous']]

            teamname ={'Arizona':'Arizona Diamondbacks','Atlanta':'Atlanta Braves', 'Baltimore':'Baltimore Orioles','Boston':'Boston Red Sox','Chi Cubs':'Chicago Cubs','Chi White Sox':'Chicago Sox','Cincinnati':'Cincinnati Reds','Cleveland':'Cleveland Guardians','Colorado':'Colorado Rockies','Detroit':'Detroit Tigers','Houston':'Houston Astros','Kansas City':'Kansas City Royals', 'LA Angels':'Los Angeles Angels', 'LA Dodgers': 'Los Angeles Dodgers','Miami':'Miami Marlins', 'Milwaukee':'Milwaukee Brewers','Minnesota':'Minnesota Twins','NY Mets':'New York Mets', 'NY Yankees':'New York Yankees', 'Oakland':'Oakland Athletics','Philadelphia':'Philadelphia Phillies','Pittsburgh':'Pittsburgh Pirates', 'San Diego': 'San Diego Padres','SF Giants': 'San Francisco Giants', 'Seattle':'Seattle Mariners', 'St. Louis':'St.Louis Cardinals', 'Tampa Bay':'Tampa Bay Rays','Texas':'Texas Rangers', 'Toronto': 'Toronto Blue Jays','Washington':'Washington Nationals'}
            self.opp_runs['Team'].replace(teamname, inplace =True)
            self.opp_runs = self.runs.replace('--', np.nan)
            self.opp_runs[['Current','Last 3','Last 1', 'Home', 'Away', 'Previous']]=self.win_pct[['Current','Last 3','Last 1', 'Home', 'Away', 'Previous']].apply(pd.to_numeric)
            
            ##################ADD ROLLING PCT FUNCTION
            self.opp_runs = self.add_rolling_pct(self.opp_runs,'opp_runs')
            #######################################################
            self.home_opp_runs = self.opp_runs.copy()
            self.away_opp_runs = self.opp_runs.copy()
            ######################################################
            ###################RENAME COLUMNS 
            self.home_opp_runs.rename(columns ={'Date':'home_D','Team':'home_', 'Current':'home_opp_Current', 'Last 3':'home_opp_3','Last 1':'home_opp_1','Home':'home_opp_Home', 'Away': 'home_opp_Away', 'Previous':'home_opp_prev','Rolling_10D_opp_runs':'Rolling_10D_opp_home','Rolling_30D_opp_runs':'Rolling_30D_opp_home'}, inplace =True)
            for col in ['home_opp_Current','home_opp_3', 'home_opp_1', 'home_opp_Home', 'home_opp_Away', 'home_opp_prev','Rolling_10D_opp_home', 'Rolling_30D_opp_home']:
                self.home_opp_runs[col] = self.home_opp_runs.groupby('home_D')[col].transform(self.normalize)
            ################################################################################

            ###################RENAME COLUMNS 
            self.away_opp_runs.rename(columns ={'Date':'away_D','Team':'away_', 'Current':'away_opp_Current', 'Last 3':'away_opp_3','Last 1':'away_opp_1','Home':'away_opp_Home', 'Away': 'away_opp_Away', 'Previous':'away_opp_prev','Rolling_10D_opp_runs':'Rolling_10D_opp_away','Rolling_30D_opp_runs':'Rolling_30D_opp_away'}, inplace =True)
            for col in ['away_opp_Current','away_opp_3', 'away_opp_1', 'away_opp_Home', 'away_opp_Away', 'away_opp_prev','Rolling_10D_opp_away', 'Rolling_30D_opp_away']:
                self.away_opp_runs[col] = self.away_opp_runs.groupby('away_D')[col].transform(self.normalize)
            ################################################################################
            
            self.home_opp_runs['home_opp_Date'] = pd.to_datetime(self.home_opp_runs['home_D'], errors='coerce').dt.date
            self.away_opp_runs['away_opp_Date'] = pd.to_datetime(self.away_opp_runs['away_D'], errors='coerce').dt.date

            self.merged_df=self.merged_df.merge(self.home_opp_runs, how='left', left_on=['home_team','game_date'], right_on=['home_','home_opp_Date'])
            self.merged_df=self.merged_df.merge(self.away_opp_runs, how='left', left_on=['away_team','game_date'], right_on=['away_','away_opp_Date'])

            self.merged_df.drop(['home_D','home_','Rolling_10D_runs_x', 'Rolling_30D_runs_x','home_opp_Date','away_D', 'away_','Rolling_10D_runs_y','Rolling_30D_runs_y', 'away_opp_Date'], axis =1, inplace =True)
            return self.merged_df
   
        

    

    def american_to_implied_probability(self,american_odds):
        """
        Convert American odds to implied probability
        """
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return abs(american_odds) / (abs(american_odds) + 100)

    def calculate_vig(self,row):
        """
        Calculate the vig given two American odds
        """
        # Calculate the implied probabilities from the odds
        prob1 = self.american_to_implied_probability(row['lowvig_home'])
        prob2 = self.american_to_implied_probability(row['lowvig_away'])

        # The vig is the excess of these probabilities over 1
        vig = prob1 + prob2 - 1
        return vig
    

    def update_columns(self):
        #combine_game_runs_opp
        self.merged_df = self.combine_game_runs_opp()

        
        
       # self.merged_df = self.merged_df.replace('--', np.nan).dropna()
       # self.merged_df = self.merged_df.drop_duplicates(subset='id', keep='last')

        self.home_cols = [col for col in self.merged_df.columns if col.endswith('_home')]
        self.away_cols = [col for col in self.merged_df.columns if col.endswith('_away')]
        self.home_vf_cols = []
        self.away_vf_cols = []
# Loop through the columns and apply the calculations
        for home_col, away_col in zip(self.home_cols, self.away_cols):
            home_prob_col = f'{home_col}_prob'
            away_prob_col = f'{away_col}_prob'
            self.home_vf_col = f'{home_col}_vf'
            self.away_vf_col = f'{away_col}_vf'

            self.merged_df[home_prob_col] = self.merged_df[home_col].apply(self.american_to_implied_probability)
            self.merged_df[away_prob_col] = self.merged_df[away_col].apply(self.american_to_implied_probability)
    
    # Calculate vig free probabilities
            total_prob = self.merged_df[home_prob_col] + self.merged_df[away_prob_col]
            self.merged_df[self.home_vf_col] = self.merged_df[home_prob_col] / total_prob
            self.merged_df[self.away_vf_col] = self.merged_df[away_prob_col] / total_prob

            self.home_vf_cols.append(self.home_vf_col)
            self.away_vf_cols.append(self.away_vf_col)

        # For columns ending with '_home_vf'
        home_vf_cols = [col for col in self.merged_df.columns if '_home_vf' in col]
        self.merged_df['max_min_diff_home_vf'] = self.merged_df[home_vf_cols].max(axis=1) - self.merged_df[home_vf_cols].min(axis=1)

        # For columns ending with '_away_vf'
        away_vf_cols = [col for col in self.merged_df.columns if '_away_vf' in col]
        self.merged_df['max_min_diff_away_vf'] = self.merged_df[away_vf_cols].max(axis=1) - self.merged_df[away_vf_cols].min(axis=1)

        #self.merged_df[]
        
        return self.merged_df
    

class Deploy_Model(Combine_Data):
    def __init__(self):
        # Call parent's init method
        super().__init__()
        self.update_columns()
        # Initialize attributes


   
        
    
    #def prepare_data(self):
     #   self.test_columns = self.merged_df.columns

       # self.merged_df = self.merged_df.rename(columns={col: col.rstrip('_x') for col in self.merged_df.columns if col.endswith('_x')})
        #self.merged_df =self.merged_df[self.merged_df['home_is_winner'] !='Unknown']
        #self.merged_df = self.merged_df[self.merged_df['game_type'] =='R']



       #self.redis_client.set('pre_model', self.merged_df.to_json(orient='records'))
        
      #  for i in self.merged_df.columns:
       #     print(i)
        
        #return self.merged_df     
        
      
    def model_output(self):
        self.df_output= model_output(self.merged_df)

        self.redis_client.set('output_data', self.df_output.to_json())
        
        return self.df_output

    







d= Deploy_Model()
print(d.model_output())

    

#d =Combine_Data()
#print(d.update_columns())
#x =d.combine_game_odds()
#x.to_csv('data_checker2.csv')