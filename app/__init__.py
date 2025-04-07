# app/__init__.py

from flask import Flask
from app.database import db  # Import db from database.py
from datetime import timedelta
from flask_mail import Mail, Message
from dotenv import load_dotenv, dotenv_values 
import os
from flask_cors import CORS

load_dotenv()

mail = Mail() # instantiate the mail class 

def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True, origins=["https://nextjsfrontendecommerce.onrender.com"], max_age=86400)  # This enables CORS for frontend

    app.config['SESSION_COOKIE_SECURE'] = True  # Send cookie only over HTTPS
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Required for cross-site cookies with credentials
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Helps prevent XSS

    # Configure the database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dothucong.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.urandom(24).hex()  # Generates a random secret key
    app.permanent_session_lifetime = timedelta(days=3)

    # Initialize the db with the app
    db.init_app(app)

    #print(os.getenv("EMAIL_ADDRESS"))
   
    # configuration of mail 
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = os.getenv("EMAIL_ADDRESS")
    app.config['MAIL_PASSWORD'] = os.getenv("EMAIL_PASSWORD")
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    
    # Initialize Mail with the app
    mail.init_app(app)

    # Import and register blueprints
    from app.routes import general_bp
    app.register_blueprint(general_bp)

    from app.admin.routes import admin_bp
    app.register_blueprint(admin_bp)

    from app.admin.changedata.routes import changedata_bp
    app.register_blueprint(changedata_bp)

    from app.customer.routes import customer_bp
    app.register_blueprint(customer_bp)

    return app
