import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .extensions import init_extensions, db
from .config import configs
from werkzeug.security import generate_password_hash, check_password_hash


def create_app(config_name='default'):
    app = Flask(__name__)
    env = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(configs[env])

    # Initialize all extensions
    init_extensions(app)


    from app.models import Admin, Registration, Payment  # Import models to register them with SQLAlchemy

    # Database table creation
    with app.app_context():
        db.create_all()

    # Register blueprints
    from app.routes import main, registration, payment, admin, auth
    app.register_blueprint(main.main_bp)
    app.register_blueprint(registration.registration_bp)
    app.register_blueprint(payment.payment_bp)
    app.register_blueprint(admin.admin_bp)
    app.register_blueprint(auth.auth_bp)


    # admin creation
    with app.app_context():
        # Check if any admin user exists
        if Admin.query.count() == 0:
            
            # Create a default admin user
            admin = Admin(
                username="admin",
                email="admin@example.com",
                password_hash=generate_password_hash("admin123")
            )
            
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists!")
    
    return app