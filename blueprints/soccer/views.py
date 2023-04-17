from flask import Blueprint, render_template

soccer_bp = Blueprint('soccer', __name__)

@soccer_bp.route('/')
def index():
    
    return render_template('soccer.html')
