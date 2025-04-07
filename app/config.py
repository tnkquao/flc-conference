import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email configuration
    # EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
    # EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
    # EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
    # EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
    # DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "conference@firstlovechurch.org")
    
    # Stripe configuration
    # STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
    # YOUR_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN') if os.environ.get('REPLIT_DEPLOYMENT') != '' else os.environ.get('REPLIT_DOMAINS', '').split(',')[0]
    
    # QR Code directory
    # QR_CODE_DIR = 'application/static/qrcodes'

class DevelopmentConfig(Config):
    SECRET_KEY = 'your-secret-key'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DEV_DATABASE_URL', 
        'postgresql://tarek:Bible63@localhost/flc_conference_dev'
    )
    # SESSION_COOKIE_SECURE = False  # Disable in development for HTTP
    TESTING = True
    # TEMPLATES_AUTO_RELOAD = True
    # EXPLAIN_TEMPLATE_LOADING = False

class ProductionConfig(Config):
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://tarek:Bible63@localhost/flc_conference'
    )
    PROPAGATE_EXCEPTIONS = True  # Better error reporting
    PREFERRED_URL_SCHEME = 'https'

configs = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}