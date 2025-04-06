import stripe
import logging
from datetime import datetime
from flask import current_app

logger = logging.getLogger(__name__)

def create_stripe_checkout(registration_data, success_url, cancel_url):
    """Create a Stripe checkout session"""
    try:
        line_items = [{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Conference Registration',
                    'description': 'First Love Church Conference Registration Fee'
                },
                'unit_amount': 5000,  # $50.00
            },
            'quantity': 1,
        }]
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            metadata={
                'registration_name': registration_data.get('name', ''),
                'registration_email': registration_data.get('email', ''),
                'registration_phone': registration_data.get('phone', ''),
            },
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        
        logger.info(f"Created Stripe checkout session: {checkout_session.id}")
        return checkout_session
    except stripe.error.StripeError as e:
        logger.error(f"Stripe API error: {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating Stripe session: {str(e)}", exc_info=True)
        raise

def verify_stripe_payment(session_id):
    """Verify a Stripe payment"""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        logger.info(f"Retrieved Stripe session: {session.id} with status: {session.payment_status}")
        return session
    except stripe.error.StripeError as e:
        logger.error(f"Stripe API error verifying payment: {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error verifying Stripe payment: {str(e)}", exc_info=True)
        raise