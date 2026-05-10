# app/routes.py
# URL routes - what happens when user visits each page

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import date, timedelta
from app.models import db, User, Shop, Order
from app.forms import LoginForm, OrderEntryForm, ShopSearchForm

# Create blueprint (logical grouping of routes)
app = Blueprint('main', __name__)

# ==================== AUTHENTICATION ====================

@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in, else login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    
    # If already logged in, redirect
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():  # Form submitted and valid
        # Find user by username
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('main.login'))
        
        # Login successful
        login_user(user)
        flash(f'Welcome {user.username}!', 'success')
        
        # Redirect to next page or dashboard
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required  # Protect this route
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

# ==================== DASHBOARD ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard - shows statistics"""
    
    # Count total shops
    total_shops = Shop.query.count()
    
    # Count total orders (today)
    today = date.today()
    today_orders = Order.query.filter_by(order_date=today).count()
    
    # Sum all order amounts
    total_orders_amount = db.session.query(db.func.sum(Order.order_amount)).scalar() or 0
    
    # Sum all payments
    total_payments = db.session.query(db.func.sum(Order.payment_amount)).scalar() or 0
    
    # Outstanding balance
    outstanding_balance = total_orders_amount - total_payments
    
    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html',
        total_shops=total_shops,
        today_orders=today_orders,
        total_orders_amount=total_orders_amount,
        total_payments=total_payments,
        outstanding_balance=outstanding_balance,
        recent_orders=recent_orders
    )

# ==================== SHOPS MODULE ====================

@app.route('/shops', methods=['GET'])
@login_required
def shops():
    """List all shops with filters"""
    
    # Get filter parameters from URL
    selected_zone = request.args.get('zone', '').strip()
    search_query = request.args.get('search', '').strip()
    
    # Start with all shops
    query = Shop.query
    
    # Filter by zone if selected
    if selected_zone:
        query = query.filter_by(zone=selected_zone)
    
    # Search by shop name if provided
    if search_query:
        query = query.filter(
            Shop.retailer_name.ilike(f'%{search_query}%')  # Case-insensitive search
        )
    
    # Get filtered shops
    shops_list = query.all()
    
    # Get unique zones for filter dropdown
    zones = db.session.query(Shop.zone).distinct().order_by(Shop.zone).all()
    zones = [z[0] for z in zones if z[0]]  # Extract zone names
    
    return render_template('shops.html',
        shops=shops_list,
        zones=zones,
        selected_zone=selected_zone,
        search_query=search_query
    )

# ==================== ORDER ENTRY MODULE ====================

@app.route('/order/new', methods=['GET', 'POST'])
@login_required
def new_order():
    """
    Two-step order entry:
    1. Search and select shop
    2. Enter order details
    """
    
    form = ShopSearchForm()
    
    # Get all zones for dropdown
    zones = db.session.query(Shop.zone).distinct().order_by(Shop.zone).all()
    zones_list = [z[0] for z in zones if z[0]]
    form.zone.choices = [('', '-- Select Zone --')] + [(z, z) for z in zones_list]
    
    # Get selected shop from URL if coming from search
    selected_shop = None
    shop_id = request.args.get('shop_id')
    if shop_id:
        selected_shop = Shop.query.get(int(shop_id))
    
    # Handle search form
    shops_list = []
    if form.validate_on_submit():
        query = Shop.query
        
        if form.zone.data:
            query = query.filter_by(zone=form.zone.data)
        
        if form.shop_name.data:
            query = query.filter(Shop.retailer_name.ilike(f'%{form.shop_name.data}%'))
        
        shops_list = query.all()
    
    return render_template('new_order.html',
        form=form,
        shops=shops_list,
        selected_shop=selected_shop
    )

@app.route('/order/<int:shop_id>/entry', methods=['GET', 'POST'])
@login_required
def order_entry(shop_id):
    """Enter order and/or payment details for selected shop"""
    
    shop = Shop.query.get_or_404(shop_id)
    form = OrderEntryForm()
    
    if form.validate_on_submit():
        # Get amounts - can be None or 0
        order_amount = form.order_amount.data or 0.0
        payment_amount = form.payment_amount.data or 0.0
        
        # Validate amounts
        if order_amount < 0:
            flash('Order Amount cannot be negative', 'danger')
            return render_template('order_entry.html', shop=shop, form=form)
        
        if payment_amount < 0:
            flash('Payment Amount cannot be negative', 'danger')
            return render_template('order_entry.html', shop=shop, form=form)
        
        # Use provided date or today's date
        order_date = form.order_date.data if form.order_date.data else date.today()
        
        # Create new order/payment record
        order = Order(
            shop_id=shop_id,
            user_id=current_user.id,
            order_date=order_date,
            order_amount=order_amount,  # Can be 0
            payment_amount=payment_amount,  # Can be 0
            payment_date=form.payment_date.data,
            notes=form.notes.data
        )
        
        # Calculate balance change
        balance_change = order_amount - payment_amount
        
        # Update shop closing balance
        shop.closing_balance += balance_change
        
        db.session.add(order)
        db.session.commit()
        
        # Show what was recorded
        message = []
        if order_amount > 0:
            message.append(f'Order: ₹{order_amount:.2f}')
        if payment_amount > 0:
            message.append(f'Payment: ₹{payment_amount:.2f}')
        
        flash(f'✅ {" + ".join(message)} recorded! Balance: ₹{shop.closing_balance:.2f}', 'success')
        return redirect(url_for('main.new_order'))
    
    return render_template('order_entry.html', shop=shop, form=form)

# ==================== VIEW ORDERS MODULE ====================

@app.route('/orders', methods=['GET'])
@login_required
def view_orders():
    """View orders - search and display"""
    
    zones = db.session.query(Shop.zone).distinct().order_by(Shop.zone).all()
    zone_list = [z[0] for z in zones if z[0]]
    
    selected_shop = None
    orders_list = []
    shops_list = []
    
    # Check if shop_id is provided (coming from shop selection)
    shop_id = request.args.get('shop_id')
    if shop_id:
        try:
            selected_shop = Shop.query.get(int(shop_id))
            if selected_shop:
                orders_list = Order.query.filter_by(shop_id=selected_shop.id).order_by(Order.order_date.desc()).all()
        except:
            pass
    
    # Handle search
    zone = request.args.get('zone', '').strip()
    shop_name = request.args.get('search', '').strip()
    
    if zone or shop_name:
        query = Shop.query
        
        if zone:
            query = query.filter_by(zone=zone)
        
        if shop_name:
            query = query.filter(Shop.retailer_name.ilike(f'%{shop_name}%'))
        
        shops_list = query.order_by(Shop.retailer_name).all()
        
        # If exactly one shop, show its orders
        if len(shops_list) == 1:
            selected_shop = shops_list[0]
            orders_list = Order.query.filter_by(shop_id=selected_shop.id).order_by(Order.order_date.desc()).all()
            shops_list = []  # Clear list so template doesn't show it
    
    return render_template('view_orders.html',
        zones=zone_list,
        selected_shop=selected_shop,
        orders=orders_list,
        shops=shops_list,
        search_zone=zone if zone else '',
        search_shop_name=shop_name if shop_name else ''
    )

@app.route('/shop/<int:shop_id>/orders')
@login_required
def shop_orders(shop_id):
    """View orders for specific shop"""
    
    shop = Shop.query.get_or_404(shop_id)
    orders_list = Order.query.filter_by(shop_id=shop_id).order_by(Order.order_date.desc()).all()
    
    return render_template('view_orders.html',
        selected_shop=shop,
        orders=orders_list
    )