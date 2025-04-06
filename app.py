import os
import uuid
import logging
import smtplib
import json
import stripe
from io import BytesIO
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
import requests
# from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import gen_salt  # For generating simple tokens
from db import db

from app.models import Registration, Admin

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__, template_folder='app/templates', 
            static_folder='app/static',  # Path to static files
            static_url_path='/static')   # URL prefix)
app.secret_key = os.environ.get("SESSION_SECRET", "church_conference_secret_key")

# Create QR code directory if it doesn't exist
QR_CODE_DIR = os.path.join(app.static_folder, 'qrcodes')
if not os.path.exists(QR_CODE_DIR):
    os.makedirs(QR_CODE_DIR)

# Stripe configuration
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
YOUR_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN') if os.environ.get('REPLIT_DEPLOYMENT') != '' else os.environ.get('REPLIT_DOMAINS', '').split(',')[0]

# Database configuration
# app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///conference.db")
app.config['SQLALCHEMY_DATABASE_URI'] =  os.environ.get("DATABASE_URL", "postgresql://tarek:Bible63@localhost/flc_conference_dev")    
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Email configuration
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "conference@firstlovechurch.org")

# Initialize extensions
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'


# Setup the Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# Initialize the db with the app
db.init_app(app)

# Create all database tables
with app.app_context():
    db.create_all()

# Formspree endpoint - we will skip this since it's not working
FORMSPREE_ENDPOINT = None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pre-registration')
def pre_registration():
    """Page to choose type of registration"""
    return render_template('pre-registration.html')

with open('app/static/countries.json', 'r') as f:
    COUNTRIES = json.load(f)


@app.route('/fl-registration', methods=['GET', 'POST'])
def fl_registration():

    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        city = request.form.get('city')
        country = request.form.get('country')
        referral = request.form.get('referral')
        is_firstlover = True
        
        # Validate form data
        if not name or not email or not phone or not country:
            flash('Please fill in all required fields', 'error')
            return render_template('registration.html')
        
        # Store registration data in session
        session['fl_registration_data'] = {
            'name': name,
            'email': email,
            'phone': phone,
            'city': city,
            'country': country,
            'referral': referral
        }
        fl_registration = Registration(
            name=name,
            email=email,
            phone=phone,
            city=city,
            country=country,
            is_firstlover=is_firstlover
        )
        db.session.add(fl_registration)
        db.session.commit()
        
        # Skip Formspree and redirect to accommodation
        flash('Registration successful!', 'success')
        return redirect(url_for('success'))
    
    return render_template('registration.html', countries=COUNTRIES)

@app.route('/nonfl-registration', methods=['GET', 'POST'])
def nonfl_registration():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        city = request.form.get('city')
        country = request.form.get('country')
        special_needs = request.form.get('special_needs')
        referral = request.form.get('referral')
        
        # Validate form data
        if not name or not email or not phone or not country:
            flash('Please fill in all required fields', 'error')
            return render_template('nonfl-registration.html')
        
        # Store registration data in session
        session['nonfl_registration'] = {
            'name': name,
            'email': email,
            'phone': phone,
            'city': city,
            'country': country,
            'special_needs': special_needs,
            'referral': referral
        }

        # Generate and store a payment access token
        session['payment_token'] = gen_salt(16)
        return redirect(url_for('payment'))
        
        # Skip Formspree and redirect to accommodation
        # flash('Registration successful!', 'success')
        # return redirect(url_for('payment'))
    
    return render_template('nonfl-registration.html', countries=COUNTRIES)


@app.route('/payment')
def payment():
    # Check if user has completed registration and accommodation
    if not session.get('payment_token') or not session.get('nonfl_registration'):
        # Redirect back to registration if not coming from there
        return redirect(url_for('nonfl_registration'))
    
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

@app.route('/checkout-session', methods=['POST'])
def create_checkout_session():
    # Check if user has completed registration and accommodation
    if 'registration' not in session:
        flash('Please complete registration and accommodation booking first', 'error')
        return redirect(url_for('nonfl_registration'))
    
    registration_data = session.get('registration', {})
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
        app.logger.error(f"Error creating checkout session: {str(e)}")
        flash('Error creating payment session. Please try again.', 'error')
        return redirect(url_for('payment'))

@app.route('/payment/success')
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
            
            # Accommodation details
            needs_accommodation=accommodation_data.get('needs_accommodation', False),
            room_type=accommodation_data.get('room_type'),
            nights=accommodation_data.get('nights'),
            room_price=accommodation_data.get('room_price'),
            
            # Payment details
            registration_fee=100.0,  # $50 registration fee
            total_paid=checkout_session.amount_total / 100,  # Convert cents to dollars
            payment_method='stripe',
            payment_id=checkout_session.id,
            payment_date=datetime.utcnow(),
            payment_status='paid'
        )
        
        # Save registration to database
        db.session.add(registration)
        db.session.commit()
        
        # Generate QR code
        generate_qr_code(registration)
        
        # Send confirmation email
        send_confirmation_email(registration)
        
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

@app.route('/payment/process', methods=['POST'])
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
                       
            # Payment details
            registration_fee=100.0,  # $50 registration fee
            total_paid=payment_details.get('amount', 100.0),
            payment_method=payment_details.get('method', 'paypal'),
            payment_id=payment_id,
            payment_date=datetime.utcnow(),
            payment_status='paid'
        )
        
        # Save registration to database
        db.session.add(registration)
        db.session.commit()
        
        # Generate QR code
        generate_qr_code(registration)
        
        # Send confirmation email
        send_confirmation_email(registration)
        
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

def send_confirmation_email(registration):
    """Send a confirmation email with QR code to the attendee"""
    if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
        app.logger.warning("Email credentials not set. Skipping email confirmation.")
        return False
    
    try:
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = DEFAULT_FROM_EMAIL
        msg['To'] = registration.email
        msg['Subject'] = "Your First Love Church Conference Registration Confirmation"
        
        # Email body with registration details
        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #0d6efd; }}
                h2 {{ color: #6c757d; }}
                .details {{ margin: 20px 0; }}
                .details p {{ margin: 5px 0; }}
                .total {{ font-weight: bold; margin-top: 20px; }}
                .qr-code {{ text-align: center; margin: 30px 0; }}
                .footer {{ margin-top: 30px; font-size: 0.9em; color: #6c757d; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Registration Confirmation</h1>
                <p>Dear {registration.name},</p>
                <p>Thank you for registering for the First Love Church Conference at Anagkazo Campus in Mampong, Eastern Region of Ghana. Your registration has been confirmed and your payment has been received.</p>
                
                <div class="details">
                    <h2>Registration Details:</h2>
                    <p><strong>Registration ID:</strong> {registration.registration_id}</p>
                    <p><strong>Name:</strong> {registration.name}</p>
                    <p><strong>Email:</strong> {registration.email}</p>
                    <p><strong>Phone:</strong> {registration.phone}</p>
                    <p><strong>Registration Fee:</strong> ${registration.registration_fee}</p>
        """
        
        # Add total cost and QR code instructions
        body += f"""
                    <p class="total"><strong>Total Amount Paid:</strong> ${registration.total_cost}</p>
                </div>
                
                <div class="qr-code">
                    <h2>Your QR Code Ticket</h2>
                    <p>Please present this QR code when checking in at the conference.</p>
                    <img src="cid:qrcode" alt="Registration QR Code" style="width: 250px;">
                </div>
                
                <div class="footer">
                    <p>We look forward to seeing you at Anagkazo Campus in Mampong!</p>
                    <p>For any questions, please contact us at conference@firstlovechurch.org</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Attach HTML body
        msg.attach(MIMEText(body, 'html'))
        
        # Attach QR code image
        if registration.qr_code:
            qr_path = os.path.join(app.static_folder, registration.qr_code)
            if os.path.exists(qr_path):
                with open(qr_path, 'rb') as qr_file:
                    qr_img = MIMEImage(qr_file.read())
                    qr_img.add_header('Content-ID', '<qrcode>')
                    msg.attach(qr_img)
        
        # Send email
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.send_message(msg)
        
        # Update registration with confirmation sent status
        registration.confirmation_sent = True
        registration.confirmation_date = datetime.utcnow()
        db.session.commit()
        
        return True
    except Exception as e:
        app.logger.error(f"Error sending confirmation email: {str(e)}")
        return False

@app.route('/success')
def success():
    registration_id = session.get('registration_id')
    registration = None
    
    if registration_id:
        registration = Registration.query.filter_by(registration_id=registration_id).first()
    
    return render_template('success.html', registration=registration)

@app.route('/qrcode/<registration_id>')
def get_qrcode(registration_id):
    """Display QR code for a registration"""
    registration = Registration.query.filter_by(registration_id=registration_id).first()
    
    if not registration or not registration.qr_code:
        flash('QR code not found', 'error')
        return redirect(url_for('index'))
    
    qr_path = os.path.join(app.static_folder, registration.qr_code)
    return send_file(qr_path, mimetype='image/png')

@app.route('/error')
def error():
    return render_template('error.html')

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            admin.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    # Get statistics for dashboard
    total_registrations = Registration.query.count()
    paid_registrations = Registration.query.filter_by(payment_status='paid').count()
    fl_registrations = Registration.query.filter_by(is_firstlover=True).count()

    # total_accommodation = Registration.query.filter_by(needs_accommodation=True).count()
    
    # Calculate revenue
    total_revenue = db.session.query(db.func.sum(Registration.total_paid)).scalar() or 0
    
    # Get recent registrations for dashboard
    recent_registrations = Registration.query.order_by(Registration.created_at.desc()).limit(5).all()
    
    # Get current date for dashboard
    now = datetime.utcnow()
    
    return render_template('admin/dashboard.html', 
                          total_registrations=total_registrations,
                          paid_registrations=paid_registrations,
                          fl_registrations=fl_registrations,
                        #   total_accommodation=total_accommodation,
                          total_revenue=total_revenue,
                          recent_registrations=recent_registrations,
                          now=now)

@app.route('/admin/registrations')
@login_required
def admin_registrations():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    status = request.args.get('status')
    is_firstlover = request.args.get('is_firstlover')
    
    # Start with base query
    query = Registration.query

    # Apply filters
    if status:
        query = query.filter_by(payment_status=status)
    
    if is_firstlover == 'true':
        query = query.filter_by(is_firstlover=True)
    
    # Get registrations with pagination
    registrations = query.order_by(Registration.created_at.desc()).paginate(page=page, per_page=per_page)
    
    return render_template('admin/registrations.html', registrations=registrations)

@app.route('/admin/registration/<registration_id>')
@login_required
def admin_registration_detail(registration_id):
    registration = Registration.query.filter_by(registration_id=registration_id).first_or_404()
    return render_template('admin/registration_detail.html', registration=registration)

@app.route('/admin/search', methods=['GET'])
@login_required
def admin_search():
    query = request.args.get('query', '')
    
    if not query:
        return redirect(url_for('admin_registrations'))
    
    # Search for registrations
    registrations = Registration.query.filter(
        db.or_(
            Registration.name.ilike(f'%{query}%'),
            Registration.email.ilike(f'%{query}%'),
            Registration.phone.ilike(f'%{query}%'),
            Registration.registration_id.ilike(f'%{query}%')
        )
    ).all()
    
    return render_template('admin/search_results.html', registrations=registrations, query=query)

@app.route('/admin/setup', methods=['GET', 'POST'])
def admin_setup():
    # Check if any admin exists
    admin_exists = Admin.query.count() > 0
    
    # If admin exists and user is not authenticated, redirect to login
    if admin_exists and not current_user.is_authenticated:
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not email or not password:
            flash('All fields are required', 'error')
        elif password != confirm_password:
            flash('Passwords do not match', 'error')
        else:
            # Create new admin
            admin = Admin(
                username=username,
                email=email,
                password_hash=generate_password_hash(password)
            )
            
            db.session.add(admin)
            db.session.commit()
            
            flash('Admin account created successfully. You can now log in.', 'success')
            return redirect(url_for('admin_login'))
    
    return render_template('admin/setup.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_message="Internal server error"), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)