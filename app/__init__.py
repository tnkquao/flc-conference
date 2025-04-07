import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .extensions import init_extensions, db
from .config import configs


def create_app(config_name='default'):
    app = Flask(__name__)
    env = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(configs[env])

    # Initialize all extensions
    init_extensions(app)


    from app import models  # Import models to register them with SQLAlchemy

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
    
    return app