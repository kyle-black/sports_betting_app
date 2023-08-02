import pandas as pd
import numpy as np
import redis 

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json
import redis
from urllib.parse import urlparse    
import os

from datetime import timedelta

def win_stats(redis_client):
    tommorow= datetime.today()+ timedelta(days=1)

    # Create a list of dates from today to 30 days ago
    dates = pd.date_range(end = tommorow, periods = 31).tolist()

    # Create an empty DataFrame
    df_win = pd.DataFrame(columns=['Date' ,'Team', 'Current','Last 3', 'Last 1', 'Home', 'Away', 'Previous'])

    for date in dates:
        # Convert date to string in the form 'YYYY-MM-DD'
        date_ = date.strftime('%Y-%m-%d')

        url_win = f"https://www.teamrankings.com/mlb/stat/win-pct-all-games?date={date_}"

        response = requests.get(url_win)

        soup = BeautifulSoup(response.content, 'html.parser')

        try:
            table = soup.find('table', class_='tr-table datatable scrollable')
            rows = table.tbody.find_all('tr')

            for row in rows:
                
                try: 
                    columns = row.find_all('td')

                    data = {
                        'Date': date_,
                        'Team': columns[1].text,
                        'Current': columns[2].text,
                        'Last 3': columns[3].text,
                        'Last 1': columns[4].text,
                        'Home': columns[5].text,
                        'Away': columns[6].text,
                        'Previous': columns[7].text
                    }
                
                    df_win = pd.concat([df_win, pd.DataFrame([data])])

                except AttributeError as e:
                    print(f'Error parsing row: {row}. Exception: {str(e)}')

        except AttributeError:
            print('Table not found on {}'.format(date_))

    redis_client.set("win_stats", df_win.to_json(orient='records'))


def run_stats(redis_client):
    tommorow= datetime.today()+ timedelta(days=1)

    # Create a list of dates from today to 30 days ago
    dates = pd.date_range(end = tommorow, periods = 31).tolist()
    # Create an empty DataFrame
    df_runs = pd.DataFrame(columns=['Date' ,'Team', 'Current','Last 3', 'Last 1', 'Home', 'Away', 'Previous'])

    for date in dates:
        # Convert date to string in the form 'YYYY-MM-DD'
        date_ = date.strftime('%Y-%m-%d')

        url_runs = f"https://www.teamrankings.com/mlb/stat/runs-per-game?date={date_}"

        response = requests.get(url_runs)

        soup = BeautifulSoup(response.content, 'html.parser')

        try:
            table = soup.find('table', class_='tr-table datatable scrollable')
            rows = table.tbody.find_all('tr')

            for row in rows:
                
                try: 
                    columns = row.find_all('td')

                    data = {
                        'Date': date_,
                        'Team': columns[1].text,
                        'Current': columns[2].text,
                        'Last 3': columns[3].text,
                        'Last 1': columns[4].text,
                        'Home': columns[5].text,
                        'Away': columns[6].text,
                        'Previous': columns[7].text
                    }
                
                    df_runs = pd.concat([df_runs, pd.DataFrame([data])])

                except AttributeError as e:
                    print(f'Error parsing row: {row}. Exception: {str(e)}')

        except AttributeError:
            print('Table not found on {}'.format(date_))

    redis_client.set("run_stats", df_runs.to_json(orient='records'))


def opp_stats(redis_client):
    tommorow= datetime.today()+ timedelta(days=1)

    # Create a list of dates from today to 30 days ago
    dates = pd.date_range(end = tommorow, periods = 31).tolist()

    # Create an empty DataFrame
    df_opps = pd.DataFrame(columns=['Date' ,'Team', 'Current','Last 3', 'Last 1', 'Home', 'Away', 'Previous'])

    for date in dates:
        # Convert date to string in the form 'YYYY-MM-DD'
        date_ = date.strftime('%Y-%m-%d')

        url_opps = f"https://www.teamrankings.com/mlb/stat/opponent-runs-per-game?date={date_}"

        response = requests.get(url_opps)

        soup = BeautifulSoup(response.content, 'html.parser')

        try:
            table = soup.find('table', class_='tr-table datatable scrollable')
            rows = table.tbody.find_all('tr')

            for row in rows:
                
                try: 
                    columns = row.find_all('td')

                    data = {
                        'Date': date_,
                        'Team': columns[1].text,
                        'Current': columns[2].text,
                        'Last 3': columns[3].text,
                        'Last 1': columns[4].text,
                        'Home': columns[5].text,
                        'Away': columns[6].text,
                        'Previous': columns[7].text
                    }
                
                    df_opps = pd.concat([df_opps, pd.DataFrame([data])])

                except AttributeError as e:
                    print(f'Error parsing row: {row}. Exception: {str(e)}')

        except AttributeError:
            print('Table not found on {}'.format(date_))

    redis_client.set("opp_stats", df_opps.to_json(orient='records'))



if __name__ in "__main__":
    url =os.getenv('REDIS_URL')
    parsed_url =urlparse(url)
    redis_client = redis.Redis(host=parsed_url.hostname, port=parsed_url.port, password=parsed_url.password)
    win_stats(redis_client)
    run_stats(redis_client)
    opp_stats(redis_client)
