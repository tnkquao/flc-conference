import os
from werkzeug.security import generate_password_hash
from app import app, db
from models import Admin

def create_admin():
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