import click
from .models import Admin

@app.cli.command("create-admin")
@click.argument("username")
@click.argument("password")
def create_admin(username, password):
    """Create an admin user"""
    admin = Admin(username=username)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    click.echo(f"Created admin user: {username}")

@click.command('deploy-init')
def deploy_init():
    """Initialize production database"""
    # from flask_migrate import upgrade
    # upgrade()