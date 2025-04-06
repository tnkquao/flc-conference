from flask import Flask, render_template, request, redirect, url_for, flash, session, Blueprint
from datetime import datetime
from flask_login import login_required
from app.models import Admin

admin_bp = Blueprint('admin',__name__, 
                template_folder='../templates',
                static_folder='../static',
                url_prefix='/admin')


# Admin routes
@admin_bp.route('/')
# @login_required
def admin_dashboard():
    # Get statistics for dashboard
    total_registrations = Registration.query.count()
    paid_registrations = Registration.query.filter_by(payment_status='paid').count()
    fl_registrations = Registration.query.filter_by(is_firstlover=True).count()
    
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
                          total_revenue=total_revenue,
                          recent_registrations=recent_registrations,
                          now=now)

@admin_bp.route('/registrations')
# @login_required
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

@admin_bp.route('/registration/<registration_id>')
# @login_required
def admin_registration_detail(registration_id):
    registration = Registration.query.filter_by(registration_id=registration_id).first_or_404()
    return render_template('admin/registration_detail.html', registration=registration)

@admin_bp.route('/search', methods=['GET'])
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
