from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.models import Admin
from app.extensions import db, login_manager

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Setup the Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            admin.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@auth_bp.route('/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('auth.admin_login'))

@auth_bp.route('/setup')
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