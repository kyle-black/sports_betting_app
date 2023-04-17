from flask import Blueprint, render_template, abort
from datetime import datetime

football_bp = Blueprint('football', __name__, url_prefix='/football')




games = [
        {
            'id': 1,
            'time': datetime.strptime('17:10', '%H:%M'),
            'home_team': {'city':'New York', 'name':'Giants'},
            'away_team': {'city':'Miami', 'name':'Dolphins'},
            'odds': {'home': -120, 'away': +100}
        },
        {
            'id': 2,
            'time': '20:30',
            'home_team': {'city':'Dallas', 'name':'Cowboys'},
            'away_team': {'city':'Houston', 'name':'Texans'},
            'odds': {'home': -110, 'away': 110}
        }
    ]
@football_bp.route('/')
def index():
    return render_template('football/football.html', games=games)




@football_bp.route('/game/<int:game_id>/')
def game(game_id):
    # You should fetch the real data for the game here
    game = next((g for g in games if g['id'] == game_id), None)
    
    if game is None:
        abort(404)
    
   
    return render_template('football/football_game.html', game=game)