from flask import Blueprint, render_template, abort
from datetime import datetime

baseball_bp = Blueprint('baseball', __name__)

games = [
    {    'id': 1,
        'time': datetime.strptime('17:10', '%H:%M'),
        'home_team': {'city': 'New York', 'name': 'Yankees'},
        'away_team': {'city': 'Boston', 'name': 'Red Sox'},
        'odds': {'home': -120, 'away': +100},
        'run_line_odds': {'home': -1.5, 'away': 1.5},
    },
    {   
        'id': 2,
        'time': datetime.strptime('19:05', '%H:%M'),
        'home_team': {'city': 'Los Angeles', 'name': 'Dodgers'},
        'away_team': {'city': 'San Francisco', 'name': 'Giants'},
        'odds': {'home': -110, 'away': 110},
        'run_line_odds': {'home': -1.5, 'away': 1.5},
    },
]

@baseball_bp.route('/')
def index():
    return render_template('baseball.html', games=games)


@baseball_bp.route('/game/<int:game_id>')
def game(game_id):
    game = next((g for g in games if g['id'] == game_id), None)
    
    if game is None:
        abort(404)
    
    return render_template('baseball_game.html', game=game)