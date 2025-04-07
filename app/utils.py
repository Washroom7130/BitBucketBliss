# app/utils.py

import os
from werkzeug.utils import secure_filename
from flask import jsonify

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')  # Adjust this path as necessary

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image(image_file, product_id):
    if image_file and allowed_file(image_file.filename):
        # Check file size
        if image_file.content_length > MAX_FILE_SIZE:
            return None, (jsonify({"error": "File size must be less than 10MB."}), 400)

        # Ensure the uploads directory for the product exists
        product_upload_folder = os.path.join(UPLOAD_FOLDER, str(product_id))
        os.makedirs(product_upload_folder, exist_ok=True)

        # Secure the filename
        filename = secure_filename(image_file.filename)
        name, ext = os.path.splitext(filename)

        # Validate filename length and characters
        if len(name) > 30 or not name.isalnum():
            return None, (jsonify({"error": "Filename must be less than 30 characters and contain only letters and numbers."}), 400)

        # Save the image
        image_path = os.path.join(product_upload_folder, filename)
        image_file.save(image_path)
        return f"{str(product_id)}/{filename}", None
    else:
        return None, (jsonify({"error": "Invalid image file."}), 400)