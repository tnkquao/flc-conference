from flask import Flask, render_template, request, redirect, url_for, flash, session, Blueprint
from datetime import datetime
from app.extensions import db
from flask_login import login_required
from app.models import Admin, Registration, Payment

admin_bp = Blueprint('admin',__name__, 
                template_folder='../templates',
                static_folder='../static',
                url_prefix='/admin')


# Admin routes
@admin_bp.route('/')
@login_required
def admin_dashboard():
    # Get statistics for dashboard
    total_registrations = Registration.query.count()
    paid_registrations = Registration.query.filter_by(payment_status='paid').count()
    fl_registrations = Registration.query.filter_by(is_firstlover=True).count()
    
    # Calculate revenue
    usd_revenue = db.session.query(db.func.sum(Payment.total_paid)).filter(Payment.currency == 'usd').scalar() or 0
    gbp_revenue = db.session.query(db.func.sum(Payment.total_paid)).filter(Payment.currency == 'gbp').scalar() or 0
    eur_revenue = db.session.query(db.func.sum(Payment.total_paid)).filter(Payment.currency == 'eur').scalar() or 0
    # Convert all revenue to USD for total revenue
    # Assuming conversion rates are 1.2 for GBP and 1.1 for EUR
    total_revenue = usd_revenue + (gbp_revenue * 1.28) + (eur_revenue * 1.09)
    # Alternatively, if you want to keep the original currency values
    # total_revenue = db.session.query(db.func.sum(Payment.total_paid)).filter(Payment.currency == 'usd').scalar() or 0
    # total_revenue = db.session.query(db.func.sum(Payment.total_paid)).filter(Payment.currency == 'gbp').scalar() or 0
    # total_revenue = db.session.query(db.func.sum(Payment.total_paid)).scalar() or 0
    
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
@login_required
def admin_registrations():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    status = request.args.get('status')
    is_firstlover = request.args.get('is_firstlover')
    
    # Start with base query
    query = db.session.query(
        Registration.id, 
        Registration.name, Registration.email, 
        Registration.phone, Registration.is_firstlover, 
        Registration.payment_status, Registration.created_at, 
        Payment.currency,
        db.func.coalesce(Payment.total_paid, 0).label('payment_amount')
    ).outerjoin(
        Payment, 
        Registration.id == Payment.registration_id
    )

    if status:
        query = query.filter(Registration.payment_status == status)

    if is_firstlover == 'true':
        query = query.filter(Registration.is_firstlover == True)

    registrations = query.order_by(Registration.created_at.desc()).paginate(page=page, per_page=per_page)
    # Get registrations with pagination
    
    return render_template('admin/registrations.html', registrations=registrations)

@admin_bp.route('/<int:registration_id>')
@login_required
def admin_registration_detail(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    payment = Payment.query.filter_by(registration_id=registration_id).first()

    return render_template(
        'admin/registration_detail.html', 
        registration=registration,
        payment=payment
    )

# @admin_bp.route('/<int:registration_id>/update', methods=['POST'])
# @login_required
# def update_reg_payment_status(registration_id):
#     registration = Registration.query.get_or_404(registration_id)
    
#     if new_status not in ['paid', 'pending', 'failed', 'refunded']:
#         flash('Invalid status', 'error')
#         return redirect(url_for('admin.admin_registration_detail', registration_id=registration_id))
    
#     registration.payment_status = new_status
#     db.session.commit()



@admin_bp.route('/search', methods=['GET'])
@login_required
def admin_search():
    query = request.args.get('query', '')
    
    if not query:
        return redirect(url_for('admin.admin_registrations'))
    
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
