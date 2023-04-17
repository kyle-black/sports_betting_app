from flask import Flask, render_template
from flask_socketio import SocketIO

from blueprints.baseball import baseball_bp
from blueprints.football import football_bp
from blueprints.basketball import basketball_bp
from blueprints.hockey import hockey_bp
from blueprints.soccer import soccer_bp
#from websocket.websocket_handler import socketio

app = Flask(__name__)
app.config.from_object('config.Config') #Update this to run config on Development

# Register blueprints
app.register_blueprint(baseball_bp, url_prefix='/baseball')
app.register_blueprint(football_bp, url_prefix='/football')
app.register_blueprint(basketball_bp, url_prefix='/basketball')
app.register_blueprint(hockey_bp, url_prefix='/hockey')
app.register_blueprint(soccer_bp, url_prefix='/soccer')

# Initialize WebSocket
#socketio.init_app(app, cors_allowed_origins="*")
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
#if __name__ == '__main__':
#    socketio.run(app, host='0.0.0.0', port=5000)