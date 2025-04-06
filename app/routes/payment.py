from flask import Blueprint, render_template, session, flash, redirect, url_for
from app.models import Payment, Registration
from app.extensions import db , stripe
# from application.services.email_service import send_confirmation_email
# from app.services.qr_service import generate_qr_code
from datetime import datetime
from flask import current_app

from app.services.email_service import send_confirmation_email
# from app.services.email_service import EmailService


payment_bp = Blueprint('payments', __name__, 
                template_folder='../templates',
                static_folder='../static',
                url_prefix='/payment')

# email_service = EmailService()


@payment_bp.route('/')
def checkout():
    # Check if user has completed registration and accommodation
    if not session.get('payment_token') or not session.get('nonfl_registration'):
        # Redirect back to registration if not coming from there
        return redirect(url_for('registrations.nonfl_registration'))
    
    # Clear the token so it can't be reused (one-time access)
    payment_token = session.pop('payment_token', None)
    print(payment_token)

    # Get registration data
    registration_data = session.get('nonfl_registration', {})
    
    return render_template('payment.html', registration=registration_data)
    """ if 'registration' not in session:
        flash('Please complete registration and accommodation booking first', 'error')
        return redirect(url_for('nonfl_registration'))
    
    registration_data = session.get('registration', {})
    accommodation_data = session.get('accommodation', {})
    
    return render_template('payment.html', 
                          registration=registration_data,
                          accommodation=accommodation_data) """

@payment_bp.route('/checkout-session', methods=['POST'])
def create_checkout_session():
    # Check if user has completed registration and accommodation
    if 'nonfl_registration' not in session:
        flash('Please complete registration and accommodation booking first', 'error')
        return redirect(url_for('nonfl_registration'))
    
    registration_data = session.get('nonfl_registration', {})
    # accommodation_data = session.get('accommodation', {})
    
    # Calculate total amount
    total_amount = 100  # Base registration fee
    line_items = [
        {
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Conference Registration',
                    'description': 'First Love Church Conference Registration Fee'
                },
                'unit_amount': 5000,  # Amount in cents (50 USD)
            },
            'quantity': 1,
        }
    ]
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            metadata={
                'registration_name': registration_data.get('name', ''),
                'registration_email': registration_data.get('email', ''),
                'registration_phone': registration_data.get('phone', ''),
                # 'needs_accommodation': str(accommodation_data.get('needs_accommodation', False)),
                # 'room_type': accommodation_data.get('room_type', ''),
                # 'nights': str(accommodation_data.get('nights', 0)),
            },
            mode='payment',
            success_url=f'https://{YOUR_DOMAIN}/payment/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'https://{YOUR_DOMAIN}/payment',
        )
        
        # Store checkout session ID in session
        session['checkout_session_id'] = checkout_session.id
        
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        current_app.logger.error(f"Error creating checkout session: {str(e)}")
        flash('Error creating payment session. Please try again.', 'error')
        return redirect(url_for('payments.checkout'))

@payment_bp.route('/success')
def payment_success():
    session_id = request.args.get('session_id')
    
    if not session_id:
        flash('Invalid payment session', 'error')
        return redirect(url_for('payment'))
    
    try:
        # Retrieve checkout session to verify payment
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        if checkout_session.payment_status != 'paid':
            flash('Payment has not been completed yet', 'error')
            return redirect(url_for('payment'))
        
        # Get registration data from session
        registration_data = session.get('registration', {})
        # accommodation_data = session.get('accommodation', {})
        
        # Create new registration record
        registration = Registration(
            name=registration_data.get('name'),
            email=registration_data.get('email'),
            phone=registration_data.get('phone'),
            city=registration_data.get('city'),
            country=registration_data.get('country'),
            special_needs=registration_data.get('special_needs'),
            referral=registration_data.get('referral'),
        )
        
        # Save registration to database
        db.session.add(registration)
        db.session.commit()

        reg_id = registration.id

        payment = Payment(
            # Payment details
            registration_fee=100.0,  # $50 registration fee
            total_paid=checkout_session.amount_total / 100,  # Convert cents to dollars
            payment_method='stripe',
            payment_id=checkout_session.id,
            payment_date=datetime.utcnow(),
            payment_status='paid',
            registration_id = reg_id
        )

        db.session.add(payment)
        db.session.commit()


        # Generate QR code
        generate_qr_code(registration)
        
        # Send confirmation email
        email_service.send_confirmation_email(registration)
        
        # Clear session data after successful payment
        session.pop('nonfl_registration', None)
        session.pop('accommodation', None)
        session.pop('checkout_session_id', None)
        
        # Store registration ID in session for success page
        session['registration_id'] = registration.registration_id
        
        flash('Payment successful! Your conference registration is complete.', 'success')
        return redirect(url_for('success'))
    except Exception as e:
        app.logger.error(f"Error processing payment: {str(e)}")
        flash('There was an error processing your payment. Please contact support.', 'error')
        return redirect(url_for('error'))

@payment_bp.route('/payment/process', methods=['POST'])
def process_payment():
    # Check if user has completed registration and accommodation
    if 'registration' not in session or 'accommodation' not in session:
        flash('Please complete registration and accommodation booking first', 'error')
        return redirect(url_for('index'))
    
    payment_id = request.form.get('payment_id')
    payment_details = request.form.get('payment_details', '{}')
    
    try:
        payment_details = json.loads(payment_details)
    except:
        payment_details = {}
    
    if payment_id:
        # Get registration data from session
        registration_data = session.get('registration', {})
        accommodation_data = session.get('accommodation', {})
        
        # Create new registration record
        registration = Registration(
            name=registration_data.get('name'),
            email=registration_data.get('email'),
            phone=registration_data.get('phone'),
            city=registration_data.get('city'),
            country=registration_data.get('country'),
            special_needs=registration_data.get('special_needs'),
            referral=registration_data.get('referral'),
        )
        
        # Save registration to database
        db.session.add(registration)
        db.session.commit()

        reg_id = registration.id

        payment = Payment(
            # Payment details
            registration_fee=100.0,  # $50 registration fee
            total_paid=checkout_session.amount_total / 100,  # Convert cents to dollars
            payment_method='stripe',
            payment_id=checkout_session.id,
            payment_date=datetime.utcnow(),
            payment_status='paid',
            registration_id = reg_id
        )

        db.session.add(payment)
        db.session.commit()

        
        # Generate QR code
        generate_qr_code(registration)
        
        # Send confirmation email
        email_service.send_confirmation_email(registration)
        
        # Clear session data after successful payment
        session.pop('nonfl_registration', None)
        session.pop('accommodation', None)
        
        # Store registration ID in session for success page
        session['registration_id'] = registration.registration_id
        
        flash('Payment successful! Your conference registration is complete.', 'success')
        return redirect(url_for('success'))
    else:
        flash('Payment processing failed. Please try again.', 'error')
        return redirect(url_for('payment'))