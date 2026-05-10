# config.py
# This file contains all configuration settings

# SECRET_KEY - Flask uses this to sign cookies (security)
# SQLALCHEMY_DATABASE_URI - Tells Flask where database is
# DEBUG = True - Shows errors (dev only, never in production)
# Separate configs for dev/production (best practice)


#################################################################################################
                    # This is the old code #
#################################################################################################


# import os
# from datetime import timedelta

# class Config:
#     """Base configuration - used for all environments"""
    
#     # Secret key - used for session security
#     # In production, use environment variable
#     SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this-in-production'
    
#     # Database configuration
#     # sqlite:/// means local file-based database
#     # credit_management.db will be created in project root
#     SQLALCHEMY_DATABASE_URI = 'sqlite:///credit_management.db'
    
#     # Don't track modifications (performance)
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
    
#     # Session settings
#     PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
#     # CSRF Protection (prevents cross-site attacks)
#     WTF_CSRF_ENABLED = True

# class DevelopmentConfig(Config):
#     """Development environment settings"""
#     DEBUG = True  # Shows errors in browser
#     TESTING = False

# class ProductionConfig(Config):
#     """Production environment settings"""
#     DEBUG = False  # Never show errors in production
#     TESTING = False

# # Dictionary to select config
# config = {
#     'development': DevelopmentConfig,
#     'production': ProductionConfig,
#     'default': DevelopmentConfig
# }



#################################################################################################
                    # This is the new code #
#################################################################################################



# config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# if os.environ.get('FLASK_ENV') == 'production':
#     load_dotenv('.env.prod')
# else:
#     load_dotenv('.env.local')

class Config:
    """Base configuration - shared by all environments"""
    
    # Secret key for session security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///credit_management.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    WTF_CSRF_ENABLED = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

class DevelopmentConfig(Config):
    """Development environment"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production environment"""
    DEBUG = False
    TESTING = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}