import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "church_conference_secret_key")

# Formspree endpoint
FORMSPREE_ENDPOINT = os.environ.get("FORMSPREE_ENDPOINT", "https://formspree.io/f/YOUR_FORM_ID")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        # Validate form data
        if not name or not email or not phone:
            flash('Please fill in all required fields', 'error')
            return render_template('registration.html')
        
        # Store registration data in session
        session['registration'] = {
            'name': name,
            'email': email,
            'phone': phone
        }
        
        # Send form data to Formspree
        try:
            response = requests.post(
                FORMSPREE_ENDPOINT,
                data={
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'form_type': 'registration'
                }
            )
            
            if response.status_code == 200:
                flash('Registration successful!', 'success')
                return redirect(url_for('accommodation'))
            else:
                flash('There was an error processing your registration. Please try again.', 'error')
        except Exception as e:
            app.logger.error(f"Error sending registration: {str(e)}")
            flash('There was an error processing your registration. Please try again.', 'error')
    
    return render_template('registration.html')

@app.route('/accommodation', methods=['GET', 'POST'])
def accommodation():
    if request.method == 'POST':
        # Check if user needs accommodation
        needs_accommodation = request.form.get('needs_accommodation') == '1'
        
        if needs_accommodation:
            # Get form data
            room_type = request.form.get('room')
            nights = request.form.get('nights')
            
            # Validate form data
            if not room_type or not nights:
                flash('Please fill in all required accommodation fields', 'error')
                return render_template('accommodation.html')
            
            # Calculate costs
            room_prices = {
                'single': 50,
                'double': 80,
                'shared': 30
            }
            
            try:
                nights = int(nights)
                room_price = room_prices.get(room_type, 0)
                total_cost = room_price * nights
                
                # Store accommodation data in session
                session['accommodation'] = {
                    'room_type': room_type,
                    'nights': nights,
                    'room_price': room_price,
                    'total_cost': total_cost,
                    'needs_accommodation': True
                }
            except ValueError:
                flash('Please enter a valid number of nights', 'error')
                return render_template('accommodation.html')
        else:
            # User doesn't need accommodation
            session['accommodation'] = {
                'needs_accommodation': False,
                'total_cost': 0
            }
        
        return redirect(url_for('payment'))
    
    return render_template('accommodation.html')

@app.route('/payment')
def payment():
    # Check if user has completed registration and accommodation
    if 'registration' not in session or 'accommodation' not in session:
        flash('Please complete registration and accommodation booking first', 'error')
        return redirect(url_for('index'))
    
    registration_data = session.get('registration', {})
    accommodation_data = session.get('accommodation', {})
    
    return render_template('payment.html', 
                          registration=registration_data,
                          accommodation=accommodation_data)

@app.route('/payment/process', methods=['POST'])
def process_payment():
    # In a real application, this would process payment
    # For this example, we'll just simulate a successful payment
    payment_id = request.form.get('payment_id')
    
    if payment_id:
        # Clear session data after successful payment
        session.pop('registration', None)
        session.pop('accommodation', None)
        
        flash('Payment successful! Your conference registration is complete.', 'success')
        return redirect(url_for('success'))
    else:
        flash('Payment processing failed. Please try again.', 'error')
        return redirect(url_for('payment'))

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/error')
def error():
    return render_template('error.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_message="Internal server error"), 500
