
from flask_login import login_required, UserMixin, login_user, logout_user
from flask import Blueprint, request, render_template, redirect, url_for, current_app, flash
from flask_login import current_user
from flask_login import LoginManager
from .forms import SignupForm, LoginForm
from .models import db, User
from . import stripe_routes

login_manager = LoginManager()

user_bp = Blueprint('user_bp', __name__)

#stripe.api_key = 'your-stripe-secret-key'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=form.remember_me.data)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))

        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html', form=form)

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@user_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        print("Form validation successful")
        user = User(username=form.username.data, subscription_status='inactive')  # User is inactive initially
        print("User object created")
        user.set_password(form.password.data)
        print("User password set")
        db.session.add(user)
        print("User added to session")
        db.session.commit()
        print("Session committed")
        flash('Congratulations, you are now a registered user! Please subscribe to access premium content.')
        return redirect(url_for('user_bp.subscription'))  # Redirects to the subscription page after successful signup
    print("Render signup template")
    return render_template('signup.html', form=form)


@user_bp.route('/subscription', methods=['GET'])
@login_required
def subscription():
    return render_template('subscription.html')

@user_bp.route('/premium_content')
@login_required
def premium_content():
    if current_user.subscription_status != 'active':
        return "You need a subscription to view this content!"
    return render_template('premium_content.html')

@user_bp.route('/charge', methods=['POST'])
@login_required
def charge():
    amount = 500  # in cents
    customer = stripe_routes.Customer.create(email=request.form['stripeEmail'], source=request.form['stripeToken'])
    stripe_routes.Charge.create(customer=customer.id, amount=amount, currency='usd', description='Flask Charge')
    current_user.subscription_status = 'active'
    db.session.commit()
    return redirect(url_for('premium_content'))