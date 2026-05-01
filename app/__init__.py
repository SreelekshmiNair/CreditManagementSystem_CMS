# app/__init__.py
# This file initializes the Flask app and extensions

from flask import Flask, render_template
from flask_login import LoginManager
from config import config
from app.models import db, User

# Initialize extensions (these need app to be created)
login_manager = LoginManager()

def create_app(config_name='default'):
    """
    Application factory - creates and configures Flask app
    
    Why factory pattern?
    - Can create multiple app instances with different configs
    - Easy testing
    - Separation of concerns
    """
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'login'  # Redirect to 'login' if not authenticated
    login_manager.login_message = 'Please log in to access this page.'
    
    # User loader - loads user from session
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register routes
    from app.routes import app as routes_bp
    app.register_blueprint(routes_bp)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    # app/__init__.py — add inside create_app(), before return app

    # ── Error Handlers ──
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()  # Roll back any broken DB transaction
        return render_template('errors/500.html'), 500
    
    return app