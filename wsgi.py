# wsgi.py
# This is used by Render's production server (Gunicorn)
# Do NOT run this locally - use run.py instead

import os
from app import create_app, db
from app.models import User, Shop, Order

# Create app with production config
app = create_app(os.environ.get('FLASK_ENV', 'production'))

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Shop': Shop, 'Order': Order}

if __name__ == '__main__':
    app.run()