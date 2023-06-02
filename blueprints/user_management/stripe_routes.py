from flask import Blueprint, request, redirect, jsonify
import stripe
import stripe.error
import requests
import json
import os
from .models import db, User  

stripe_bp = Blueprint('stripe_bp', __name__)

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@stripe_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': os.getenv('STRIPE_PRICE_ID'),
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=os.getenv('SITE_DOMAIN') +
            '/success.html?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=os.getenv('SITE_DOMAIN') + '/cancel.html',
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        print(e)
        return "Server error", 500

@stripe_bp.route('/webhook', methods=['POST'])
def webhook_received():
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    request_data = json.loads(request.data)

    if webhook_secret:
        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret)
            data = event['data']
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            return str(e), 400
        except Exception as e:
            return str(e), 500
    else:
        data = request_data['data']
        event_type = request_data['type']

    data_object = data['object']
    print('event ' + event_type)

    if event_type == 'checkout.session.completed':
        print('🔔 Payment succeeded!')
        user = User.query.filter_by(stripe_id=data_object['customer']).first()
        if user:
            user.subscription_status = 'active'
            db.session.commit()

    elif event_type == 'customer.subscription.created':
        print('Subscription created %s', data_object['id'])
        user = User.query.filter_by(stripe_id=data_object['customer']).first()
        if user:
            user.subscription_status = 'active'
            user.stripe_subscription_id = data_object['id']
            db.session.commit()

    elif event_type == 'customer.subscription.deleted':
        print('Subscription canceled: %s', data_object['id'])
        user = User.query.filter_by(stripe_id=data_object['customer']).first()
        if user:
            user.subscription_status = 'inactive'
            db.session.commit()

    return jsonify({'status': 'success'})