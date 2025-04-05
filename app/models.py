import uuid
from datetime import datetime
from db import db
from flask_login import UserMixin

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    is_firstlover = db.Column(db.Boolean, default=False, nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    special_needs = db.Column(db.Text, nullable=True)
    referral = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Define the relationship with the PaymentData model
    payments = db.relationship('Payment', backref='registration', lazy=True)
    
    # Email confirmation
    """ confirmation_sent = db.Column(db.Boolean, default=False)
    confirmation_date = db.Column(db.DateTime, nullable=True) """
    
    # QR Code (we'll store the path or URL to the QR code)
    # qr_code = db.Column(db.String(255), nullable=True)
    
    # Admin notes
    # admin_notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Registration {self.name}>'
    
    # @property
    # def total_accommodation_cost(self):
    #     if not self.needs_accommodation or not self.room_price or not self.nights:
    #         return 0
    #     return self.room_price * self.nights
    
    # @property
    # def total_cost(self):
    #     return self.registration_fee + self.total_accommodation_cost
    
    # @property
    # def is_paid(self):
    #     return self.payment_status == 'paid'
    
    def to_dict(self):
        return {
            'id': self.id,
            'registration_id': self.registration_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'city': self.city,
            'country': self.country,
            'special_needs': self.special_needs,
            'referral': self.referral,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'total_cost': self.total_cost,
            'total_paid': self.total_paid,
            'payment_method': self.payment_method,
            'payment_id': self.payment_id,
            'payment_date': self.payment_date.strftime('%Y-%m-%d %H:%M:%S') if self.payment_date else None,
            'payment_status': self.payment_status,
            'is_paid': self.is_paid,
            'confirmation_sent': self.confirmation_sent,
            'confirmation_date': self.confirmation_date.strftime('%Y-%m-%d %H:%M:%S') if self.confirmation_date else None,
        }

class Payment(db.Model):
    # Payment details
    id = db.Column(db.Integer, primary_key=True)
    registration_fee = db.Column(db.Float, nullable=False)  # $50 registration fee
    total_paid = db.Column(db.Float, nullable=True)
    payment_method = db.Column(db.String(20), nullable=True)
    payment_id = db.Column(db.String(100), nullable=True)
    payment_date = db.Column(db.DateTime, nullable=True)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed, refunded

    # Foreign key linking back to RegistrationData
    registration_id = db.Column(db.Integer, db.ForeignKey('registration.id'), nullable=False)

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Admin {self.username}>'