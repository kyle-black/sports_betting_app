import sqlite3
import pandas as pd
import requests
import json



conn = sqlite3.connect('mlb_games.db')
cursor= conn.cursor()



url = "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/?regions=us&markets=h2h&oddsFormat=american&apiKey=7a29fdc77828ef42a5c65e00dffc586f"
response = requests.get(url)


data = response.json()

game_list =[]
for idx, i in enumerate(data):
    i_d = idx
    
    time = i['commence_time']
    away_team = i['away_team']
    home_team =i['home_team']
    game ={'game_id':i_d,'time':time, 'away_team':away_team, 'home_team':home_team}
    game_list.append(game)

print(game_list)

df = pd.DataFrame(game_list)

df.to_sql('upcoming_games', conn, if_exists='replace',index=False)

conn.commit()
conn.close()

#print(df)