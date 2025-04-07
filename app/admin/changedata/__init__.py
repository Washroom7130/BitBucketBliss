# app/admin/changedata/__init__.py

from flask import Blueprint

changedata_bp = Blueprint('changedata', __name__)

from app.admin.changedata import routes  # Import routes after blueprint is defined