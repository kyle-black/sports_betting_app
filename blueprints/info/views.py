from flask import Blueprint, render_template, abort, current_app, request, session
from datetime import datetime
import json
from statistics import median
from datetime import datetime

import jsonify

info_bp = Blueprint('info', __name__, url_prefix='/info')


@info_bp.route('/EV', methods=['GET', 'POST'])
def ev_bet():
    

    return render_template('info/evbet.html')