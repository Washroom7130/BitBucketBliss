# app/admin/changedata/routes.py

from flask import Blueprint, jsonify, request
from app.database import db
from app.models import KhachHang, NhanVien, SanPham, TaiKhoan, DanhMuc, SanPham, DonHang, ChiTietDonHang, DanhGia  # Import your models
from app.admin.routes import admin_required, admin_or_staff_required
from datetime import datetime
from app.utils import upload_image
import bcrypt, uuid, os

changedata_bp = Blueprint('changedata', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'uploads')  # Adjust this path as necessary

def validate_category(category_id):
    return db.session.query(DanhMuc).filter_by(MaDanhMuc=category_id).first() is not None

@changedata_bp.route('/admin/change-customer-status/<int:customer_id>', methods=['POST'])
@admin_required
def change_customer_status(customer_id):
    # Get the new status from the request JSON body
    data = request.get_json()
    new_status = data.get('status')

    # Validate the new status
    if new_status is None or not isinstance(new_status, bool):
        return jsonify({"error": "Status must be a boolean (true/false)"}), 400

    # Check if the customer exists
    customer = db.session.get(KhachHang, customer_id)
    if not customer:
        return jsonify({"error": "Không tìm thấy khách hàng"}), 404

    # Update the customer's status
    customer.TrangThai = new_status
    db.session.commit()

    return jsonify({"message": "Customer status updated successfully"}), 200

@changedata_bp.route('/admin/add-new-staff', methods=['POST'])
@admin_required
def add_new_staff():
    data = request.get_json()

    #print(data)

    # Extract parameters
    staff_name = data.get('staff_name')
    staff_birthday = data.get('staff_birthday')
    staff_email = data.get('staff_email')
    staff_phone_num = data.get('staff_phone_num')
    staff_password = data.get('staff_password')
    confirm_staff_password = data.get('confirm_staff_password')

    # Validate required parameters
    if not all([staff_name, staff_birthday, staff_email, staff_phone_num, staff_password, confirm_staff_password]):
        return jsonify({"error": "Hãy nhập đủ thông tin!"}), 400

    try:
        staff_birthday = datetime.strptime(staff_birthday, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Định dạng ngày không hợp lệ. Vui lòng sử dụng định dạng YYYY-MM-DD."}), 400

    # Check if passwords match
    if staff_password != confirm_staff_password:
        return jsonify({"error": "Mật khẩu không khớp!"}), 400

    # Hash the password
    hashed_password = bcrypt.hashpw(staff_password.encode('utf-8'), bcrypt.gensalt(rounds=10))

    # Create a new staff member
    new_staff = NhanVien(
        TenNV=staff_name,
        NgaySinh=staff_birthday,
        Email=staff_email,
        Sdt=staff_phone_num,
        TrangThai=True  # Assuming you want to set the status to active by default
    )

    # Add to NhanVien table
    db.session.add(new_staff)
    db.session.commit()  # Commit to get the MaNV

    # Create an account for the new staff member
    new_account = TaiKhoan(
        MaTK=str(uuid.uuid4()),  # Link to the newly created staff ID
        TenDangNhap=staff_email,  # Use email as username for simplicity
        MatKhau=hashed_password.decode('utf-8'),  # Store the hashed password
        VaiTro='staff',  # Assuming a default role
        MaNV=new_staff.MaNV
    )

    # Add to TaiKhoan table
    db.session.add(new_account)
    db.session.commit()  # Commit the account creation

    return jsonify({"message": "New staff member added successfully."}), 201

@changedata_bp.route('/admin/change-staff-data/<int:staff_id>', methods=['POST'])
@admin_required
def change_staff_data(staff_id):
    data = request.get_json()

    #print(data)

    # Check if the staff member exists
    staff_member = db.session.get(NhanVien, staff_id)
    if not staff_member:
        return jsonify({"error": "Không tìm thấy nhân viên"}), 404

    # Check if the account exists
    account = db.session.query(TaiKhoan).filter_by(MaNV=staff_id).first()
    if not account:
        return jsonify({"error": "Không tìm thấy tài khoản nhân viên"}), 404

    # Update fields if provided in the request
    if 'staff_name' in data:
        staff_member.TenNV = data['staff_name']
    
    if 'staff_birthday' in data:
        try:
            staff_member.NgaySinh = datetime.strptime(data['staff_birthday'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Định dạng ngày không hợp lệ. Vui lòng sử dụng định dạng YYYY-MM-DD."}), 400

    if 'staff_email' in data:
        staff_member.Email = data['staff_email']
        account.TenDangNhap = data['staff_email']  # Update TenTaiKhoan to the new email

    if 'staff_phone-num' in data:
        staff_member.Sdt = data['staff_phone-num']

    if 'staff_status' in data:
        if isinstance(data['staff_status'], bool):
            staff_member.TrangThai = data['staff_status']
        else:
            return jsonify({"error": "Staff status must be a boolean (true/false)."}), 400

    if 'new_password' in data or 'confirm_new_password' in data:
        # Extract new password fields
        new_password = data.get('new_password')
        confirm_new_password = data.get('confirm_new_password')

        # Validate required parameters
        if not new_password or not confirm_new_password:
            return jsonify({"error": "Hãy nhập đủ mật khẩu mới."}), 400

        # Check if passwords match
        if new_password != confirm_new_password:
            return jsonify({"error": "Mật khẩu không khớp!"}), 400

        # Hash the new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt(rounds=10))

        # Update the password in the TaiKhoan table
        account.MatKhau = hashed_password.decode('utf-8')

    # Commit the changes to the database
    db.session.commit()

    return jsonify({"message": "Staff member data updated successfully."}), 200

@changedata_bp.route('/admin/change-staff-password/<int:staff_id>', methods=['POST'])
@admin_required
def change_staff_password(staff_id):
    data = request.get_json()

    # Check if the staff member exists
    account = db.session.query(TaiKhoan).filter_by(MaTK=staff_id).first()
    if not account:
        return jsonify({"error": "Staff account not found."}), 404

    # Extract new password fields
    new_password = data.get('new_password')
    confirm_new_password = data.get('confirm_new_password')

    # Validate required parameters
    if not new_password or not confirm_new_password:
        return jsonify({"error": "Both new password fields are required."}), 400

    # Check if passwords match
    if new_password != confirm_new_password:
        return jsonify({"error": "Passwords do not match."}), 400

    # Hash the new password
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt(rounds=10))

    # Update the password in the TaiKhoan table
    account.MatKhau = hashed_password.decode('utf-8')

    # Commit the changes to the database
    db.session.commit()

    return jsonify({"message": "Password updated successfully."}), 200

@changedata_bp.route('/staff/add-category', methods=['POST'])
@admin_or_staff_required
def add_category():
    data = request.get_json()

    # Extract and validate the category name
    category_name = data.get('category_name')
    if not category_name:
        return jsonify({"error": "Hãy nhập tên danh mục"}), 400

    # Create a new category instance
    new_category = DanhMuc(
        TenDanhMuc=category_name  # Adjust this according to your Category model
    )

    # Add the new category to the database
    db.session.add(new_category)
    db.session.commit()

    return jsonify({"message": "Category added successfully."}), 201

@changedata_bp.route('/staff/change-category-data/<int:category_id>', methods=['POST'])
@admin_or_staff_required
def change_category_data(category_id):
    data = request.get_json()

    # Check if the category exists
    category = db.session.get(DanhMuc, category_id)
    if not category:
        return jsonify({"error": "Không tìm thấy danh mục"}), 404

    # Extract and validate the new category name
    category_name = data.get('category_name')
    if not category_name:
        return jsonify({"error": "Hãy nhập tên danh mục"}), 400

    # Update the category name
    category.TenDanhMuc = category_name  # Adjust according to your model field name

    # Commit the changes to the database
    db.session.commit()

    return jsonify({"message": "Category name updated successfully."}), 200

@changedata_bp.route('/staff/add-product', methods=['POST'])
@admin_or_staff_required
def add_product():
    data = request.form

    # Extract product data
    product_name = data.get('product_name')
    description = data.get('description')
    price = data.get('price')
    quantity = data.get('quantity')
    category_id = data.get('category_id')
    image_file = request.files.get('image')

    # Validate product data
    if not all([product_name, price, quantity, category_id]):
        return jsonify({"error": "Hãy nhập đủ thông tin!"}), 400

    # Validate category ID
    if not validate_category(category_id):
        return jsonify({"error": "Mã danh mục không tồn tại"}), 400

    # Validate price and quantity
    try:
        price = float(price)
        quantity = int(quantity)
    except ValueError:
        return jsonify({"error": "Giá và số phải là số dương"}), 400

    if float(price) < 0 or int(quantity) < 0:
        return jsonify({"error": "Giá và số phải là số dương"}), 400

    # Create a new product instance
    new_product = SanPham(
        TenSP=product_name,
        MoTa=description,
        GiaBan=price,
        SoLuong=quantity,
        MaDanhMuc=category_id
    )

    # Add the new product to the database
    db.session.add(new_product)
    db.session.commit()

    # Upload the image
    if image_file:
        relative_image_path, error_response = upload_image(image_file, new_product.MaSP)
        if error_response:
            return error_response
        new_product.MaAnh = relative_image_path  # Update the image path

    db.session.commit()    

    return jsonify({"message": "Product added successfully."}), 201

@changedata_bp.route('/staff/change-product-data/<int:product_id>', methods=['POST'])
@admin_or_staff_required
def change_product_data(product_id):
    data = request.form

    # Check if the product exists
    product = db.session.get(SanPham, product_id)
    if not product:
        return jsonify({"error": "Không tìm thấy sản phẩm."}), 404

    # Extract product data
    product_name = data.get('product_name')
    description = data.get('description')
    price = data.get('price')
    quantity = data.get('quantity')
    category_id = data.get('category_id')
    image_file = request.files.get('image')

    # Update fields only if they are provided
    if product_name:
        product.TenSP = product_name
        
    if description:
        product.MoTa = description
        
    if price and float(price) >= 0:
        try:
            product.GiaBan = float(price)
        except ValueError:
            return jsonify({"error": "Giá và số phải là số dương."}), 400
        
    if quantity and int(quantity) >= 0:
        try:
            product.SoLuong = int(quantity)
        except ValueError:
            return jsonify({"error": "Giá và số phải là số dương."}), 400

    if category_id:
        # Validate category ID
        if not validate_category(category_id):
            return jsonify({"error": "Mã danh mục không tồn tại."}), 400
        product.MaDanhMuc = category_id

    # Handle image upload if a new image is provided
    if image_file:
        old_path = product.MaAnh
        relative_image_path, error_response = upload_image(image_file, product_id)
        if error_response:
            return error_response
        product.MaAnh = relative_image_path  # Update the image path
        if old_path != relative_image_path:
            os.remove(old_path)

    # Commit the changes to the database
    db.session.commit()

    return jsonify({"message": "Product data updated successfully."}), 200

@changedata_bp.route('/staff/change-order-status/<int:order_id>', methods=['POST'])
@admin_or_staff_required
def change_order_status(order_id):
    data = request.json
    new_status = data.get('status')

    # Define accepted status progression
    status_progression = {
        "Chờ xử lí": "Xác nhận",
        "Xác nhận": "Đang giao",
        "Đang giao": "Đã giao",
        "Đã hủy": None  # No further progression allowed from canceled orders
    }

    # Check if the order exists
    order = db.session.get(DonHang, order_id)
    if not order:
        return jsonify({"error": "Không tìm thấy đơn hàng."}), 404

    # Prevent changing status if it's already "Đã giao"
    if order.TrangThai == "Đã giao":
        return jsonify({"error": "Không thể thay đổi trạng thái của đơn hàng đã giao."}), 400

    # Determine allowed next statuses based on current status
    allowed_statuses = []
    if order.TrangThai in status_progression:
        next_status = status_progression[order.TrangThai]
        if next_status:  # if there's a defined next status
            allowed_statuses.append(next_status)
    # Allow cancellation from any status (except already delivered)
    allowed_statuses.append("Đã hủy")

    # Validate new_status against allowed statuses
    if new_status not in allowed_statuses:
        return jsonify({"error": "Hãy thay đổi trạng thái đơn hàng lần lượt."}), 400

    # Update order status
    order.TrangThai = new_status

    # If the order is canceled, add back the product quantities
    if new_status == "Đã hủy":
        order_details = ChiTietDonHang.query.filter_by(MaDonHang=order_id).all()
        for detail in order_details:
            product = db.session.get(SanPham, detail.MaSP)
            if product:
                product.SoLuong += detail.SoLuongSP

    # Commit the changes to the database
    db.session.commit()

    return jsonify({"message": "Order status updated successfully."}), 200

@changedata_bp.route('/staff/delete-category/<int:category_id>', methods=['DELETE'])
@admin_or_staff_required
def delete_category(category_id):
    # Check if the category exists
    category = db.session.get(DanhMuc, category_id)
    if not category:
        return jsonify({"error": "Không tìm thấy danh mục."}), 404

    # Check if there are any products linked to this category
    products = SanPham.query.filter_by(MaDanhMuc=category_id).all()
    if products:
        return jsonify({"error": "Không được xóa danh mục có sản phẩm liên kết."}), 400

    # Delete the category
    db.session.delete(category)
    db.session.commit()

    return jsonify({"message": "Category deleted successfully."}), 200


@changedata_bp.route('/staff/delete-product/<int:product_id>', methods=['DELETE'])
@admin_or_staff_required
def delete_product(product_id):
    # Check if the product exists
    product = db.session.get(SanPham, product_id)
    if not product:
        return jsonify({"error": "Không tìm thấy sản phẩm."}), 404

    # Set the quantity to -1 instead of deleting
    product.SoLuong = -1
    db.session.commit()

    return jsonify({"message": "Product marked as deleted successfully."}), 200

@changedata_bp.route('/staff/delete-comment/<int:comment_id>', methods=['DELETE'])
@admin_or_staff_required
def delete_comment(comment_id):
    # Check if the comment exists
    comment = db.session.get(DanhGia, comment_id)  # Assuming Comment is the model class for comments
    if not comment:
        return jsonify({"error": "Không tìm thấy đánh giá."}), 404

    # Delete the comment from the database
    db.session.delete(comment)
    db.session.commit()

    return jsonify({"message": "Comment deleted successfully."}), 200