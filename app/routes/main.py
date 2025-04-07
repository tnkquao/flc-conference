from flask import Blueprint, render_template, session

main_bp = Blueprint('main',__name__, 
                template_folder='../templates',
                static_folder='../static')

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/pre-registration')
def pre_registration():
    """Page to choose type of registration"""
    return render_template('pre-registration.html')

@main_bp.route('/success')
def success():
    registration_id = session.get('registration_id')
    registration = None
    
    if registration_id:
        registration = Registration.query.filter_by(registration_id=registration_id).first()
    
    return render_template('success.html', registration=registration)

@main_bp.route('/error')
def error():
    return render_template('error.html')