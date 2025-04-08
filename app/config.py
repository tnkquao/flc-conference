import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email configuration
    EMAIL_HOST = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    EMAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    EMAIL_USE_TLS = True
    EMAIL_USE_SSL = False
    EMAIL_HOST_USER = os.environ.get("MAIL_USERNAME", "tarek.quao@gmail.com")
    EMAIL_HOST_PASSWORD = os.environ.get("MAIL_APP_PASSWORD", "ebuaxmqkpjamlown")
    DEFAULT_FROM_EMAIL = os.environ.get("MAIL_DEFAULT_SENDER", "")
    
    # Stripe configuration
    # STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
    # YOUR_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN') if os.environ.get('REPLIT_DEPLOYMENT') != '' else os.environ.get('REPLIT_DOMAINS', '').split(',')[0]
    
    # QR Code directory
    # QR_CODE_DIR = 'application/static/qrcodes'

class DevelopmentConfig(Config):
    SECRET_KEY = 'your-secret-key'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL')
    # SESSION_COOKIE_SECURE = False  # Disable in development for HTTP
    TESTING = True
    STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')  # For webhook verification
    # TEMPLATES_AUTO_RELOAD = True
    # EXPLAIN_TEMPLATE_LOADING = False

class ProductionConfig(Config):
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    PROPAGATE_EXCEPTIONS = True  # Better error reporting
    PREFERRED_URL_SCHEME = 'https'
    SESSION_COOKIE_SECURE = True

configs = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}