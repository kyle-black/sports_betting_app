from flask import Blueprint, render_template, abort, current_app
from datetime import datetime
import json

football_bp = Blueprint('football', __name__, url_prefix='/football')

def calculate_best_odds_and_books(games):
    for game in games:
        best_home_odds = None
        best_away_odds = None
        best_home_book = ""
        best_away_book = ""

        for bookmaker in game['bookmakers']:
            h2h_market = None
            for market in bookmaker['markets']:
                if market['key'] == 'h2h':
                    h2h_market = market
                    break

            if h2h_market:
                home_odds = h2h_market['outcomes'][0]['price']
                away_odds = h2h_market['outcomes'][1]['price']

                if best_home_odds is None or (home_odds > 0 and home_odds > best_home_odds) or (home_odds < 0 and home_odds < best_home_odds):
                    best_home_odds = home_odds
                    best_home_book = bookmaker['title']

                if best_away_odds is None or (away_odds > 0 and away_odds > best_away_odds) or (away_odds < 0 and away_odds < best_away_odds):
                    best_away_odds = away_odds
                    best_away_book = bookmaker['title']

        game['best_home_book'] = best_home_book
        game['best_home_odds'] = best_home_odds
        game['best_away_book'] = best_away_book
        game['best_away_odds'] = best_away_odds

    return games

@football_bp.route('/NFL')
def index():
    redis_client = current_app.extensions["redis"]
    games_data = redis_client.get("nfl_data")
    nfl_games =[]
    date_format = "%Y-%m-%dT%H:%M:%SZ"
    if games_data:
        games = json.loads(games_data)

        for game in games:
            if game['sport_title'] == "NFL":
                game['commence_time'] = datetime.strptime(game['commence_time'], date_format)
                
                total_home_odds = 0
                total_away_odds = 0
                bookmaker_count = 0

                for bookmaker in game['bookmakers']:
                    h2h_market = next((market for market in bookmaker['markets'] if market['key'] == 'h2h'), None)
                    if h2h_market:
                        bookmaker_count += 1
                        total_home_odds += h2h_market['outcomes'][0]['price']
                        total_away_odds += h2h_market['outcomes'][1]['price']

                if bookmaker_count > 0:
                    game['avg_home_odds'] = round(total_home_odds / bookmaker_count)
                    game['avg_away_odds'] = round(total_away_odds / bookmaker_count)

                nfl_games.append(game)                

        nfl_games = calculate_best_odds_and_books(nfl_games)

    else:
        nfl_games =[]
    return render_template('football/football.html', games=nfl_games)

@football_bp.route('/game/<string:game_id>/')
def game(game_id):
    redis_client = current_app.extensions["redis"]
    games_data = redis_client.get("nfl_data")

    if games_data:
        games = json.loads(games_data)
        game = next((g for g in games if g['id'] == game_id), None)

        if game is None:
            abort(404)

        # Prepare the bookmakers data
        bookmakers = []
        for bookmaker in game['bookmakers']:
            h2h_market = next((market for market in bookmaker['markets'] if market['key'] == 'h2h'), None)
            if h2h_market:
                bookmaker_data = {
                    'title': bookmaker['title'],
                    'home_odds': h2h_market['outcomes'][0]['price'],
                    'away_odds': h2h_market['outcomes'][1]['price']
                }
                bookmakers.append(bookmaker_data)
                print("Bookmaker data: ", bookmaker_data)  # Debugging print statement

        game['bookmakers'] = bookmakers
        print("Game data: ", game)  # Debugging print statement

        return render_template('football/football_game.html', game=game)

    else:
        abort(404)