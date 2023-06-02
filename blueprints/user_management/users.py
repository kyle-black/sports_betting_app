
from flask_login import login_required, UserMixin, login_user, logout_user
from flask import Blueprint, request, render_template, redirect, url_for, current_app, flash
from flask_login import current_user
from flask_login import LoginManager
from .forms import SignupForm, LoginForm
from .models import db, User
from . import stripe_routes
import stripe
import jsonify
from urllib.parse import quote


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
        email = form.email.data
        password = form.password.data
        print(f"Email: {email}, Password: {password}")  # Debug print

        user = User.query.filter_by(email=email).first()
        if user:
            print(f"User found: {user}")  # Debug print
            if user.check_password(password):
                login_user(user, remember=form.remember_me.data)
                flash('Logged in successfully.', 'success')
                return redirect(url_for('index'))
            else:
                print("Password check failed")  # Debug print
        else:
            print("No user found")  # Debug print

        flash('Invalid email or password.', 'error')
    else:
        print(f"Form validation failed with errors: {form.errors}")  # Debug print

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
        user = User(email=form.email.data, subscription_status='inactive')  # User is inactive initially
        print("User object created")
        user.set_password(form.password.data)
        print("User password set")

        # Create a new Stripe customer and set the customer id for the user
        try:
            customer = stripe.Customer.create(email=user.email)
            user.stripe_id = customer.id
            print("Stripe customer created, customer id set for user")
        except Exception as e:
            print(f"Error creating Stripe customer: {str(e)}")
            flash('Error creating Stripe customer. Please try again.', 'error')
            return render_template('signup.html', form=form)

        db.session.add(user)
        print("User added to session")
        db.session.commit()
        print("Session committed")
        login_user(user)
        flash('Congratulations, you are now a registered user! Please subscribe to access premium content.')
        return redirect(url_for('user_bp.subscription'))  # Redirects to the subscription page after successful signup
    else:
        print(form.errors)
    print("Render signup template")
    return render_template('signup.html', form=form)

@user_bp.route('/success')
def success():
    x= "test"
    return render_template('success.html', successful=x)


@user_bp.route('/subscription', methods=['GET'])
@login_required
def subscription():
    email_encoded = quote(current_user.email)  # URL encoding the email
    stripe_url = f"https://buy.stripe.com/test_dR64jl8Vg6mx5ry000?prefilled_email={email_encoded}"
    return render_template('subscription.html', stripe_url=stripe_url)

@user_bp.route('/premium_content')
@login_required
def premium_content():
    if current_user.subscription_status != 'active':
        return "You need a subscription to view this content!"
    return render_template('premium_content.html')

@user_bp.route('/charge', methods=['POST'])
@login_required
def charge():
    # Create a checkout session with the subscription price
    try:
        checkout_session = stripe.checkout.Session.create(
            customer=current_user.stripe_id,  # Use stored Stripe customer ID
            line_items=[
                {
                    'price': 'your_price_id',  # replace with your price id
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=url_for('user_bp.success', _external=True) +
            '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('user_bp.subscription', _external=True),
        )
        return jsonify({'checkout_url': checkout_session.url}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400