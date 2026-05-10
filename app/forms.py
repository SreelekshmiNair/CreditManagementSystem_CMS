# app/forms.py
# WTForms - handles form validation and CSRF protection

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Optional
from datetime import date

class LoginForm(FlaskForm):
    """Login form - username and password"""
    
    username = StringField('Username',
        validators=[
            DataRequired(message='Username is required'),
            Length(min=2, max=80, message='Username must be 2-80 characters')
        ])
    
    password = PasswordField('Password',
        validators=[
            DataRequired(message='Password is required')
        ])
    
    submit = SubmitField('Login')

class OrderForm(FlaskForm):
    """Form for entering new order"""
    
    order_date = DateField('Order Date',
        validators=[Optional()],
        default=date.today())  # Default to today
    
    order_amount = FloatField('Order Amount (₹)',
        validators=[Optional()],
        default=0.0) #default to 0.0 so it doesn't show as empty in the form, but user can change it
    
    payment_amount = FloatField('Payment Received (₹)',
        validators=[Optional()],
        default=0.0)
    
    payment_date = DateField('Payment Date',
        validators=[Optional()])
    
    notes = TextAreaField('Notes',
        validators=[Optional(), Length(max=500)])
    
    submit = SubmitField('Save Order')

class ShopSearchForm(FlaskForm):
    """Form for searching shops"""
    
    zone = SelectField('Zone',
        choices=[],  # Will be populated dynamically
        validators=[Optional()])
    
    shop_name = StringField('Shop Name',
        validators=[Optional(), Length(max=120)])
    
    submit = SubmitField('Search')