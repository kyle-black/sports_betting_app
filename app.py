from flask import Flask, render_template, session, redirect
from flask_socketio import SocketIO
from flask_redis import FlaskRedis
import os

from blueprints.baseball import baseball_bp
from blueprints.football import football_bp
from blueprints.basketball import basketball_bp
from blueprints.hockey import hockey_bp
from blueprints.soccer import soccer_bp
from blueprints.user_management.users import user_bp
from blueprints.user_management.stripe_routes import stripe_bp
from config import Config
from data_fetcher import fetch_and_store_data
from flask_login import LoginManager
from blueprints.user_management.users import login_manager
from blueprints.info import info_bp


from blueprints.user_management.models import db
from flask_login import current_user

import requests
import json
import jsonify
app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig') #Update this to run config on Development

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test2.db'
redis_client = FlaskRedis(app)

db.init_app(app)


with app.app_context():
    db.create_all()



login_manager.init_app(app)






print("Calling fetch_and_store_data...")
fetch_and_store_data(redis_client)

# Register blueprints
app.register_blueprint(baseball_bp, url_prefix='/baseball')
app.register_blueprint(football_bp, url_prefix='/football')
app.register_blueprint(basketball_bp, url_prefix='/basketball')
app.register_blueprint(hockey_bp, url_prefix='/hockey')
app.register_blueprint(soccer_bp, url_prefix='/soccer')
app.register_blueprint(user_bp, url_prefix='/users')
app.register_blueprint(stripe_bp, url_prefix='/stripe')
app.register_blueprint(info_bp, url_prefix='/info')

@app.route('/')
def index():
    return render_template('index.html')


@app.context_processor
def inject_user():
    return dict(user=current_user)




if __name__ == '__main__':
    app.run()
