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
    config = current_app.config

    """Send a confirmation email with QR code to the attendee"""
    if not config.get('EMAIL_HOST_USER') or not config.get('EMAIL_HOST_PASSWORD'):
        logger.warning("Email credentials not set. Skipping email confirmation.")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = config['DEFAULT_FROM_EMAIL']
        msg['To'] = registration.email
        msg['Subject'] = "Your First Love Conference Registration Confirmation"
        
        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #0d6efd; }}
                h2 {{ color: #6c757d; }}
                .details {{ margin: 20px 0; }}
                .details p {{ margin: 5px 0; }}
                .total {{ font-weight: bold; margin-top: 20px; }}
                .qr-code {{ text-align: center; margin: 30px 0; }}
                .footer {{ margin-top: 30px; font-size: 0.9em; color: #6c757d; text-align: center; }}
            </style>
        </head>
        <body>
            <h1>Registration Confirmation</h1>
            <p>Dear {registration.name},</p>
            <p>Thank you for registering for the conference! <br>
            Kindly see your country/city pastor for payment details.</p>
            <p> We look forward to having you join us for a special time in God's presence! </p>
            <br>
            <span>With Love</span><br>
            <span>The First Love Conference</span>
            <!-- Rest of your email template -->
        </body>
        </html>
        """
        
        print(body)

        msg.attach(MIMEText(body, 'html'))
        
        # if registration.qr_code:
        #     qr_path = os.path.join(current_app.static_folder, registration.qr_code)
        #     if os.path.exists(qr_path):
        #         with open(qr_path, 'rb') as qr_file:
        #             qr_img = MIMEImage(qr_file.read())
        #             qr_img.add_header('Content-ID', '<qrcode>')
        #             msg.attach(qr_img)
        
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


def send_confirmation_email_nonfl(registration, payment):
    config = current_app.config

    """Send a confirmation email with QR code to the attendee"""
    if not config.get('EMAIL_HOST_USER') or not config.get('EMAIL_HOST_PASSWORD'):
        app.logger.warning("Email credentials not set. Skipping email confirmation.")
        return False
    
    try:
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = config['DEFAULT_FROM_EMAIL']
        msg['To'] = registration.email
        msg['Subject'] = "Your First Love Conference Registration Confirmation"
        
        # Email body with registration details
        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #0d6efd; }}
                h2 {{ color: #6c757d; }}
                .details {{ margin: 20px 0; }}
                .details p {{ margin: 5px 0; }}
                .total {{ font-weight: bold; margin-top: 20px; }}
                .qr-code {{ text-align: center; margin: 30px 0; }}
                .footer {{ margin-top: 30px; font-size: 0.9em; color: #6c757d; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Registration Confirmation</h1>
                <p>Dear {registration.name},</p>
                <p>Thank you for registering for the First Love Church Conference at the First Love Center in East Legon, Accra, Ghana. Your registration has been confirmed and your payment has been received.</p>
                
                <div class="details">
                    <h2>Registration Details:</h2>
                    <p><strong>Registration ID:</strong> {registration.registration_id}</p>
                    <p><strong>Name:</strong> {registration.name}</p>
                    <p><strong>Email:</strong> {registration.email}</p>
                    <p><strong>Phone:</strong> {registration.phone}</p>
                    <p><strong>Registration Fee:</strong> ${payment.total_paid}</p>
        """
        
        # Add total cost and QR code instructions
        # <div class="qr-code">
        #     <h2>Your QR Code Ticket</h2>
        #     <p>Please present this QR code when checking in at the conference.</p>
        #     <img src="cid:qrcode" alt="Registration QR Code" style="width: 250px;">
        # </div>
        
        body += f"""
                <div class="footer">
                    <p>We look forward to seeing you at the First Love Center in Accra!</p>
                    <p>For any questions, please contact us at conference@firstlovechurch.org</p>
                </div>
            </div>
        </body>
        </html>
        """
        print(body)
        
        # Attach HTML body
        msg.attach(MIMEText(body, 'html'))
        
        # Attach QR code image
        # if registration.qr_code:
        #     qr_path = os.path.join(app.static_folder, registration.qr_code)
        #     if os.path.exists(qr_path):
        #         with open(qr_path, 'rb') as qr_file:
        #             qr_img = MIMEImage(qr_file.read())
        #             qr_img.add_header('Content-ID', '<qrcode>')
        #             msg.attach(qr_img)
        
        # Send email
        with smtplib.SMTP(config['EMAIL_HOST'], config['EMAIL_PORT']) as server:
            server.starttls()
            server.login(config['EMAIL_HOST_USER'], config['EMAIL_HOST_PASSWORD'])
            server.send_message(msg)
        
        # Update registration with confirmation sent status
        registration.confirmation_sent = True
        registration.confirmation_date = datetime.utcnow()
        db.session.commit()
        
        return True
    except Exception as e:
        app.logger.error(f"Error sending confirmation email: {str(e)}")
        return False