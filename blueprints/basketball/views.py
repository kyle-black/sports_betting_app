from flask import Blueprint, render_template, abort
from datetime import datetime

basketball_bp = Blueprint('basketball', __name__, url_prefix='/basketball')




games = [
        {
            'id': 1,
            'time': datetime.strptime('17:10', '%H:%M'),
            'home_team': {'city':'New York', 'name':'Knicks'},
            'away_team': {'city':'Boston', 'name':'Celtics'},
            'odds': {'home': -120, 'away': +100}
        },
        {
            'id': 2,
            'time': '20:30',
            'home_team': {'city':'Detroit', 'name':'Pistons'},
            'away_team': {'city':'Toronto', 'name':'Raptors'},
            'odds': {'home': -110, 'away': 110}
        }
    ]
@basketball_bp.route('/')
def index():
    return render_template('basketball/basketball.html', games=games)




@basketball_bp.route('/game/<int:game_id>/')
def game(game_id):
    # You should fetch the real data for the game here
    game = next((g for g in games if g['id'] == game_id), None)
    
    if game is None:
        abort(404)
    
   
    return render_template('basketball/basketball_game.html', game=game)