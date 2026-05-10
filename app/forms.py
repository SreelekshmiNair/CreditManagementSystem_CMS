# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional, Length, ValidationError
from datetime import date

class LoginForm(FlaskForm):
    """Login form"""
    
    username = StringField('Username',
        validators=[DataRequired(), Length(min=2, max=80)])
    
    password = PasswordField('Password',
        validators=[DataRequired()])
    
    submit = SubmitField('Login')


class OrderEntryForm(FlaskForm):
    """Form for entering order and/or payment"""
    
    order_date = DateField('Order Date',
        validators=[Optional()],
        default=date.today())
    
    order_amount = FloatField('Order Amount (₹)',
        validators=[Optional()])
    
    payment_date = DateField('Payment Date',
        validators=[Optional()])
    
    payment_amount = FloatField('Payment Amount (₹)',
        validators=[Optional()],
        default=0.0)
    
    notes = TextAreaField('Notes',
        validators=[Optional(), Length(max=500)])
    
    submit = SubmitField('Save Order')
    
    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False
        
        # Get the values
        order_amt = self.order_amount.data
        payment_amt = self.payment_amount.data
        
        # At least one amount must be provided
        if (not order_amt or order_amt == 0) and (not payment_amt or payment_amt == 0):
            self.order_amount.errors.append('Either Order Amount or Payment Amount is required')
            return False
        
        return True


class ShopSearchForm(FlaskForm):
    """Form for searching shops"""

    zone = SelectField('Zone',
        choices=[],
        validators=[Optional()])

    shop_name = StringField('Shop Name',
        validators=[Optional(), Length(max=120)])

    submit = SubmitField('Search')