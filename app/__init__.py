from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
from .extensions import init_extensions
from config import configs

# db = SQLAlchemy
# migrate = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(configs[config_name])

    # Initialize all extensions
    init_extensions(app)

    # db.init_app(app)
    # migrate.init_app(app, db)

    from app import models  # Import models to register them with SQLAlchemy
    
    # Register blueprints
    from app.routes import main, registration, payment, admin, auth
    app.register_blueprint(main.main_bp)
    app.register_blueprint(registration.registration_bp)
    app.register_blueprint(payment.payment_bp)
    app.register_blueprint(admin.admin_bp)
    app.register_blueprint(auth.auth_bp)
    
    return app