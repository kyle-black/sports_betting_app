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

from flask_migrate import Migrate  # new
from blueprints.user_management.models import db
from flask_login import current_user

import requests
import json
import jsonify
from config import config_dict
import logging
from logging.handlers import RotatingFileHandler

def create_app(config_name):

    app = Flask(__name__)
    app.config.from_object(config_dict[config_name])

    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/your_application.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Your application startup')



    
    redis_client = FlaskRedis(app)

    db.init_app(app)
    migrate = Migrate(app, db)  # new

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
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    return app

app = create_app(os.getenv('FLASK_CONFIG', 'default'))

if __name__ == '__main__':
    app.run()