# app/admin/__init__.py

from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

from app.admin import routes  # Import routes after blueprint is defined