# run.py
# This is how you start the app

#################################################################################################
                    # This is the old code #
#################################################################################################



# import os
# from app import create_app, db
# from app.models import User, Shop, Order

# # Create app instance
# app = create_app(os.environ.get('FLASK_ENV') or 'default')

# # Shell context for debugging
# @app.shell_context_processor
# def make_shell_context():
#     """Allows using models in flask shell"""
#     return {'db': db, 'User': User, 'Shop': Shop, 'Order': Order}

# if __name__ == '__main__':
#     # Run app on port 5000
#     # debug=True: auto-reload on code changes, error page in browser
#     app.run(debug=True, port=5000)




#################################################################################################
                    # This is the new code #
#################################################################################################


# run.py
import os
from app import create_app, db
from app.models import User, Shop, Order

# Create app with environment-based config
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

@app.shell_context_processor
def make_shell_context():
    """Allow using models in flask shell"""
    return {'db': db, 'User': User, 'Shop': Shop, 'Order': Order}

if __name__ == '__main__':
    # Run locally with debug enabled
    app.run(debug=True, port=5000)
