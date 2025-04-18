from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
# from flask_caching import Cache
# from flask_mail import Mail
import stripe
# from flask_wtf.csrf import CSRFProtect



# csrf = CSRFProtect()
# Initialize extensions with no app bound initially
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
# limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])
# cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
# mail = Mail()

def init_extensions(app):
    """Initialize all extensions with the Flask application"""

    # Database initialization
    db.init_app(app)


    # Login manager setup
    login_manager.init_app(app)
    login_manager.login_view = 'auth.admin_login'
    login_manager.login_message_category = 'warning'
    
    # Migration setup
    migrate.init_app(app, db)
    
    # Rate limiting
    # limiter.init_app(app)
    
    # Caching
    # cache.init_app(app)
    
    # Email
    # mail.init_app(app)
    
    # Stripe configuration
    stripe.api_key = app.config.get('STRIPE_SECRET_KEY')
    stripe.api_version = '2024-06-20'  # Pin to specific API version
    
    # Register teardown context
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()