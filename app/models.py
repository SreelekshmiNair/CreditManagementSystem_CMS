# app/models.py
# Database models - defines table structure

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Create database object (will initialize in __init__.py)
db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User table - stores login information"""
    
    __tablename__ = 'users'  # Table name in database
    
    id = db.Column(db.Integer, primary_key=True)  # Auto-increment ID
    username = db.Column(db.String(80), unique=True, nullable=False)  # Must be unique
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)  # Hashed, never plain text
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Auto timestamp
    
    def set_password(self, password):
        """Hash password before storing"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if entered password matches stored hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        """String representation for debugging"""
        return f'<User {self.username}>'

class Shop(db.Model):
    """Shop table - stores shop/retailer information"""
    
    __tablename__ = 'shops'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Retailer Information
    retailer_name = db.Column(db.String(120), nullable=False)
    retailer_code = db.Column(db.String(100))
    retailer_unique_code = db.Column(db.String(100), unique=True)
    retailer_status = db.Column(db.String(50), default='Active')
    retailer_address = db.Column(db.Text)
    contact_number = db.Column(db.String(30))
    
    # Salesman Information
    salesman_code = db.Column(db.String(50))
    salesman_name = db.Column(db.String(120))
    
    # Route Information
    route_code = db.Column(db.String(50))
    route_name = db.Column(db.String(120))
    
    # Zone & Channel Information
    zone = db.Column(db.String(80), nullable=False)  # Used for filtering
    channel_group = db.Column(db.String(80))
    channel = db.Column(db.String(80))
    channel_subtype = db.Column(db.String(80))
    
    # Financial Information
    closing_balance = db.Column(db.Float, default=0.0)  # Total credit owed
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to orders (one shop has many orders)
    orders = db.relationship('Order', backref='shop', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Shop {self.retailer_name}>'

class Order(db.Model):
    """Order table - stores daily transactions"""
    
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)  # Link to shop
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Who entered it
    
    order_date = db.Column(db.Date, nullable=False)  # Date of order
    order_amount = db.Column(db.Float, nullable=False)  # Amount ordered
    payment_amount = db.Column(db.Float, default=0.0)  # Amount paid
    payment_date = db.Column(db.Date)  # Date payment received
    notes = db.Column(db.Text)  # Any notes
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # When recorded
    
    # Relationship to user
    user = db.relationship('User', backref='orders')
    
    def __repr__(self):
        return f'<Order {self.id} - {self.shop.retailer_name}>'