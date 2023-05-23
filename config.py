import os
import secrets

PRODUCTION_REDIS_USERNAME = os.getenv('PRODUCTION_REDIS_USERNAME')
PRODUCTION_REDIS_PASSWORD = os.getenv('PRODUCTION_REDIS_PASSWORD')
PRODUCTION_REDIS_HOST = os.getenv('PRODUCTION_REDIS_HOST')
PRODUCTION_REDIS_PORT = os.getenv('PRODUCTION_REDIS_PORT')



class Config(object):
    REDIS_URL = "redis://localhost:6379/0"
    DEBUG = False
    TESTING = False
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'test2.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    

class ProductionConfig(Config):
    REDIS_URL = f'''redis://{PRODUCTION_REDIS_USERNAME}:{PRODUCTION_REDIS_PASSWORD}@{PRODUCTION_REDIS_HOST}:{PRODUCTION_REDIS_PORT}/0'''
