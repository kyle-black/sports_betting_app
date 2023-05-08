from flask import Blueprint, render_template, abort, current_app
from datetime import datetime
import json
from statistics import median

import jsonify

baseball_bp = Blueprint('baseball', __name__, url_prefix='/baseball')

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
                for outcome in h2h_market['outcomes']:
                    if outcome['name'] == game['home_team']:
                        home_odds = outcome['price']
                    elif outcome['name'] == game['away_team']:
                        away_odds = outcome['price']

                if best_home_odds is None or (home_odds > 0 and (best_home_odds < 0 or home_odds > best_home_odds)) or (home_odds < 0 and home_odds > best_home_odds):
                    best_home_odds = home_odds
                    best_home_book = bookmaker['title']

                if best_away_odds is None or (away_odds > 0 and (best_away_odds < 0 or away_odds > best_away_odds)) or (away_odds < 0 and away_odds > best_away_odds):
                    best_away_odds = away_odds
                    best_away_book = bookmaker['title']

        game['best_home_book'] = best_home_book
        game['best_home_odds'] = best_home_odds
        game['best_away_book'] = best_away_book
        game['best_away_odds'] = best_away_odds

    return games

def probability_to_american_odds(probability):
    if probability < 0 or probability > 1:
        raise ValueError("Probability must be between 0 and 1.")
    
    if probability >= 0.5:
        american_odds = -1 * (probability / (1 - probability)) * 100
    else:
        american_odds = (1 / probability) * 100 - 100
    
    return round(american_odds)

def american_odds_to_probability(american_odds):
    if american_odds >= 0:
        probability = 100 / (american_odds + 100)
    else:
        probability = -1 * american_odds / (-1 * american_odds + 100)
    return probability


def calculate_expected_value_percentage(games):
    for game in games:
        if game['away_prediction_american'] is not None and game['best_away_odds'] is not None:
            game['away_expected_value'] = calculate_expected_value(game['away_prediction_american'], game['best_away_odds'])

        if game['home_prediction_american'] is not None and game['best_home_odds'] is not None:
            game['home_expected_value'] = calculate_expected_value(game['home_prediction_american'], game['best_home_odds'])

    return games

def calculate_expected_value(ai_odds, best_odds):
    ai_probability = american_odds_to_probability(ai_odds)
    best_probability = american_odds_to_probability(best_odds)

    if ai_odds > 0 and best_odds > 0:
        expected_value = (ai_probability * (best_odds / 100)) - (1 - ai_probability)
    elif ai_odds < 0 and best_odds < 0:
        expected_value = (ai_probability * (-100 / best_odds)) - (1 - ai_probability)
    else:
        if ai_odds > 0 and best_odds < 0:
            expected_value = ((1 - ai_probability) * (-100 / best_odds)) - ai_probability
        elif ai_odds < 0 and best_odds > 0:
            expected_value = (ai_probability * (best_odds / 100)) - (1 - ai_probability)
        else:
            expected_value = -1  # This case should never happen, but just in case

    return round(expected_value * 100, 2)






@baseball_bp.route('/simple_test')
def simple_test():
    return "This is a simple test route."

@baseball_bp.route('/MLB')
def index():
    redis_client = current_app.extensions["redis"]
    games_data = redis_client.get("mlb_data")
    predictions_data = redis_client.get('mlb_predictions')
    
    mlb_games = []
    date_format = "%Y-%m-%dT%H:%M:%SZ"
    
    if predictions_data:
        predictions = json.loads(predictions_data)
       # print(f"Predictions: {predictions}")  # Debug statement
    else:
        predictions = []
    
    if games_data:
        games = json.loads(games_data)

        for game in games:
            game['away_prediction_american'] = None
            game['home_prediction_american'] = None
            if game['sport_title'] == "MLB":
                game['commence_time'] = datetime.strptime(game['commence_time'], date_format)

                home_odds_list = []
                away_odds_list = []

                for bookmaker in game['bookmakers']:
                    h2h_market = next((market for market in bookmaker['markets'] if market['key'] == 'h2h'), None)
                    if h2h_market:
                        for outcome in h2h_market['outcomes']:
                            if outcome['name'] == game['home_team']:
                                home_odds_list.append(outcome['price'])
                            elif outcome['name'] == game['away_team']:
                                away_odds_list.append(outcome['price'])
            if home_odds_list and away_odds_list:
                    game['median_home_odds'] = round(median(home_odds_list))
                    game['median_away_odds'] = round(median(away_odds_list))

            game_prediction = None

            for game_id, pred in predictions.items():
                    if str(game['id']) == game_id:
                        game_prediction = pred
                        break

            if game_prediction:
                    game['away_prediction'] = round((game_prediction['probs'][0] *100),1)
                    game['away_prediction_american'] = probability_to_american_odds(game_prediction['probs'][0] ) 
                    game['home_prediction'] = round((game_prediction['probs'][1] * 100),1)
                    game['home_prediction_american'] = probability_to_american_odds(game_prediction['probs'][1] ) 
            else:
                    game['away_prediction'] = None
                    game['home_prediction'] = None

            mlb_games.append(game)

        mlb_games = calculate_best_odds_and_books(mlb_games)
        mlb_games = calculate_expected_value_percentage(mlb_games)

    else:
        mlb_games = []

    return render_template('baseball/baseball.html', games=mlb_games)

        #return y_predict

@baseball_bp.route('/game/<string:game_id>/')
def game(game_id):
    redis_client = current_app.extensions["redis"]
    games_data = redis_client.get("mlb_data")

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
                home_odds = None
                away_odds = None
                for outcome in h2h_market['outcomes']:
                    if outcome['name'] == game['home_team']:
                        home_odds = outcome['price']
                    elif outcome['name'] == game['away_team']:
                        away_odds = outcome['price']

                bookmaker_data = {
                    'title': bookmaker['title'],
                    'home_odds': home_odds,
                    'away_odds': away_odds
                }
                bookmakers.append(bookmaker_data)
                print("Bookmaker data: ", bookmaker_data)  # Debugging print statement

        game['bookmakers'] = bookmakers
        print("Game data: ", game)  # Debugging print statement

        return render_template('baseball/baseball_game.html', game=game)

    else:
        abort(404)

@baseball_bp.route('/test')
def test_data():
    preds = model2.predictions
    return preds


