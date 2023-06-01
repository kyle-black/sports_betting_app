from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()





class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    subscription_status = db.Column(db.String(64), default='inactive')
    stripe_id = db.Column(db.String(128))  # new column for Stripe customer ID
    stripe_subscription_id = db.Column(db.String(128))  # Stripe subscription ID
    stripe_payment_method = db.Column(db.String(128))  # Stripe default payment method

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
