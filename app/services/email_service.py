import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
import os
from flask import current_app
from app.extensions import db

logger = logging.getLogger(__name__)

def send_confirmation_email(registration):
    """Send a confirmation email with QR code to the attendee"""
    config = current_app.config
    
    if not config.get('EMAIL_HOST_USER') or not config.get('EMAIL_HOST_PASSWORD'):
        logger.warning("Email credentials not set. Skipping email confirmation.")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = config['DEFAULT_FROM_EMAIL']
        msg['To'] = registration.email
        msg['Subject'] = "Your First Love Church Conference Registration Confirmation"
        
        body = f"""
        <html>
        <body>
            <h1>Registration Confirmation</h1>
            <p>Dear {registration.name},</p>
            <p>Thank you for registering for the conference!</p>
            <!-- Rest of your email template -->
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        if registration.qr_code:
            qr_path = os.path.join(current_app.static_folder, registration.qr_code)
            if os.path.exists(qr_path):
                with open(qr_path, 'rb') as qr_file:
                    qr_img = MIMEImage(qr_file.read())
                    qr_img.add_header('Content-ID', '<qrcode>')
                    msg.attach(qr_img)
        
        with smtplib.SMTP(config['EMAIL_HOST'], config['EMAIL_PORT']) as server:
            server.starttls()
            server.login(config['EMAIL_HOST_USER'], config['EMAIL_HOST_PASSWORD'])
            server.send_message(msg)
        
        registration.confirmation_sent = True
        registration.confirmation_date = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Confirmation email sent to {registration.email}")
        return True
    except Exception as e:
        logger.error(f"Error sending confirmation email to {registration.email}: {str(e)}", exc_info=True)
        return False