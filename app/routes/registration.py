from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import json
from werkzeug.security import gen_salt
from app.extensions import db
from app.models import Registration
from app.services.email_service import send_confirmation_email
# from app.services.email_service import EmailService

# email_service = EmailService()

from flask import current_app

registration_bp = Blueprint('registrations', __name__, 
                template_folder='../templates',
                static_folder='../static',
                url_prefix='/registration')


with open('app/static/countries.json', 'r') as f:
    COUNTRIES = json.load(f)


@registration_bp.route('/first-love', methods=['GET', 'POST'])
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

        # registration_data = session.get('registration', {})
        send_confirmation_email(fl_registration)
        
        # Skip Formspree and redirect to accommodation
        flash('Registration successful!', 'success')
        return redirect(url_for('main.success'))
    
    return render_template('registration.html', countries=COUNTRIES)

@registration_bp.route('/non-first-love', methods=['GET', 'POST'])
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
        return redirect(url_for('payments.checkout'))
        
        # Skip Formspree and redirect to accommodation
        # flash('Registration successful!', 'success')
        # return redirect(url_for('payment'))
    
    return render_template('nonfl-registration.html', countries=COUNTRIES)

