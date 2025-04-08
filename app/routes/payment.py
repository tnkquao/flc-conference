from flask import Blueprint, render_template, session, flash, redirect, url_for
from app.models import Payment, Registration
from app.extensions import db , stripe
from app.services.email_service import send_confirmation_email_nonfl
# from app.services.qr_service import generate_qr_code
from datetime import datetime
from flask import current_app
from flask import request

# from app.services.email_service import EmailService


payment_bp = Blueprint('payments', __name__, 
                template_folder='../templates',
                static_folder='../static',
                url_prefix='/payment')

# email_service = EmailService()

# @payment_bp.route('/checkout-session', methods=['POST'])
def create_checkout_session():
    # Check if user has completed registration and accommodation
    if 'nonfl_registration' not in session:
        flash('Please complete registration and accommodation booking first', 'error')
        return redirect(url_for('nonfl_registration'))
    
    registration_data = session.get('nonfl_registration', {})
    currency = registration_data['currency']

    # Define prices per currency (in smallest units: cents/pence)
    price_map = {
        'usd': 10000,  # $100.00
        'eur': 10000,  # €100.00
        'gbp': 10000,  # £100.00
    }
    
    # Calculate total amount
    if currency not in price_map:
        currency = 'usd'  # Fallback

    line_items = [
        {
            'price_data': {
                'currency': currency,
                'product_data': {
                    'name': 'Conference Registration',
                    'description': 'First Love Conference Registration Fee'
                },
                'unit_amount': price_map[currency],  # Amount
            },
            'quantity': 1,
        }
    ]

    # success_url = url_for(
    #     'payments.payment_success',
    #     session_id='{{CHECKOUT_SESSION_ID}}',
    #     _external=True)
    success_url = f"{request.url_root}payment/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = url_for('payments.cancel', _external=True)
    
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
            success_url=success_url,
            cancel_url=cancel_url,
        )
        
        # Store checkout session ID in session
        session['checkout_session_id'] = checkout_session.id
        
        return checkout_session
    except Exception as e:
        current_app.logger.error(f"Error creating checkout session: {str(e)}")
        # flash('Error creating payment session. Please try again.', 'error')
        return redirect(url_for('payments.checkout'))


@payment_bp.route('/')
def checkout():
    # Check if user has completed registration and accommodation
    if not session.get('payment_token') or not session.get('nonfl_registration'):
        # Redirect back to registration if not coming from there
        return redirect(url_for('registrations.nonfl_registration'))
    
    # Clear the token so it can't be reused (one-time access)
    payment_token = session.pop('payment_token', None)

    # Get registration data
    registration_data = session.get('nonfl_registration', {})
    print(registration_data)
    try:
        checkout_session = create_checkout_session()
        
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        current_app.logger.error(f"Checkout error: {str(e)}")
        return redirect(url_for('registrations.nonfl_registration'))

    return render_template('payment.html', registration=registration_data)


@payment_bp.route('/success')
def payment_success():
    print("Incoming request args:", request.args)
    session_id = request.args.get('session_id')
    
    if not session_id:
        flash('Invalid payment session', 'error')
        return redirect(url_for('payments.checkout'))
    
    try:
        # Retrieve checkout session to verify payment
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        print(checkout_session)
        if checkout_session.payment_status != 'paid':
            flash('Payment has not been completed yet', 'error')
            return redirect(url_for('payment'))
        
    #     # Get registration data from session
        registration_data = session.get('nonfl_registration', {})
        print(registration_data)
        
        print(registration_data)
        # Create new registration record
        registration = Registration(
            name=registration_data.get('name'),
            email=registration_data.get('email'),
            phone=registration_data.get('phone'),
            city=registration_data.get('city'),
            country=registration_data.get('country'),
            special_needs=registration_data.get('special_needs'),
            referral=registration_data.get('referral'),
            payment_status=checkout_session.payment_status
        )

        print(registration)
        
        # Save registration to database
        db.session.add(registration)
        db.session.commit()

        reg_id = registration.id

        payment = Payment(
            # Payment details
            total_paid=checkout_session.amount_total / 100,  
            payment_method='stripe',
            payment_id=checkout_session.id,
            payment_date=datetime.utcnow(),
            payment_status=checkout_session.payment_status,
            currency=checkout_session.currency,
            registration_id = reg_id
        )
        print(payment)
        db.session.add(payment)
        db.session.commit()


    #     # Generate QR code
    #     generate_qr_code(registration)
        
    #     # Send confirmation email
        send_confirmation_email_nonfl(registration, payment)
        
    #     # Clear session data after successful payment
        session.pop('nonfl_registration', None)
        session.pop('payment_token', None)

        session.pop('checkout_session_id', None)
        
        # Store registration ID in session for success page
        session['registration_id'] = registration.registration_id
        
        flash('Payment successful! Your conference registration is complete.', 'success')
        return redirect(url_for('main.success'))
    except Exception as e:
        current_app.logger.error(f"Error processing payment: {str(e)}")
        flash('There was an error processing your payment. Please contact support.', 'error')
        return redirect(url_for('main.error'))

@payment_bp.route('/cancel', methods=['GET'])
def cancel():
    """
    Handle canceled payment
    """
    return render_template('payment/cancel.html')

@payment_bp.route('/process', methods=['POST'])
def process_payment():
    # Check if user has completed registration and accommodation
    if 'registration' not in session:
        flash('Please complete registration first', 'error')
        return redirect(url_for('main.index'))
    
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
            # payment_status='paid',
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
        return redirect(url_for('payments.success'))
    else:
        flash('Payment processing failed. Please try again.', 'error')
        return redirect(url_for('payment'))

@payment_bp.route('/qrcode/<registration_id>')
def get_qrcode(registration_id):
    """Display QR code for a registration"""
    registration = Registration.query.filter_by(registration_id=registration_id).first()
    
    if not registration or not registration.qr_code:
        flash('QR code not found', 'error')
        return redirect(url_for('main.index'))
    
    qr_path = os.path.join(current_app.static_folder, registration.qr_code)
    return send_file(qr_path, mimetype='image/png')