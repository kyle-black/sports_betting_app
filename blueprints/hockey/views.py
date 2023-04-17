from flask import Blueprint, render_template, abort
from datetime import datetime

hockey_bp = Blueprint('hockey', __name__, url_prefix='/hockey')




games = [
        {
            'id': 1,
            'time': datetime.strptime('17:10', '%H:%M'),
            'home_team': {'city':'New York', 'name':'Rangers'},
            'away_team': {'city':'Calgary', 'name':'Flames'},
            'odds': {'home': -120, 'away': +100}
        },
        {
            'id': 2,
            'time': '20:30',
            'home_team': {'city':'Dallas', 'name':'Stars'},
            'away_team': {'city':'Florida', 'name':'Panthers'},
            'odds': {'home': -110, 'away': 110}
        }
    ]
@hockey_bp.route('/')
def index():
    return render_template('hockey/hockey.html', games=games)




@hockey_bp.route('/game/<int:game_id>/')
def game(game_id):
    # You should fetch the real data for the game here
    game = next((g for g in games if g['id'] == game_id), None)
    
    if game is None:
        abort(404)
    
   
    return render_template('hockey/hockey_game.html', game=game)