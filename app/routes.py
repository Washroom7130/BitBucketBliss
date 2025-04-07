# app/routes.py

from flask import Blueprint, request, jsonify, session, Flask, send_from_directory, abort
from app.database import db
from app.models import KhachHang, TaiKhoan, SanPham, DanhMuc, DanhGia, QuanLy, NhanVien, GioHang, Token, ChiTietDonHang
import bcrypt, uuid, os, random, string
from datetime import datetime, timedelta
from app import mail
from dotenv import load_dotenv, dotenv_values
from flask_mail import Message

general_bp = Blueprint('general', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')

load_dotenv()

@general_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Extract parameters
    name = data.get('name')
    birthday = data.get('birthday')
    email = data.get('email')
    phone_number = data.get('phone')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    # Validate parameters
    if not all([name, birthday, email, phone_number, password, confirm_password]):
        return jsonify({"error": "Xin hãy nhập đầy đủ thông tin!"}), 400

    if password != confirm_password:
        return jsonify({"error": "Mật khẩu không khớp!"}), 400

    # Convert birthday from string to date object
    try:
        birthday_date = datetime.strptime(birthday, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Định dạng ngày không hợp lệ. Vui lòng sử dụng định dạng YYYY-MM-DD."}), 400

    # Insert into KhachHang table
    #customer_id = str(uuid.uuid4())
    new_customer = KhachHang(
        TenKH=name,
        NgaySinh=birthday_date,
        Email=email,
        Sdt=phone_number
    )

    db.session.add(new_customer)
    db.session.commit()

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=10)).decode('utf-8')

    # Insert into TaiKhoan table
    new_account = TaiKhoan(
        MaTK=str(uuid.uuid4()),  # Generate a new UUID
        TenDangNhap=email,  # Use email as username
        MatKhau=hashed_password,
        VaiTro='user',
        MaKH=new_customer.MaKH,
        MaQL=None,
        MaNV=None
    )

    db.session.add(new_account)
    db.session.commit()

    new_cart = GioHang(
        MaKH=new_customer.MaKH
    )

    db.session.add(new_cart)
    db.session.commit()

    # Generate a random token
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
    expiration_time = datetime.now() + timedelta(minutes=30)

    # Insert into Token table
    new_token = Token(
        Token=token,
        LoaiToken="VerifyEmail",
        ThoiDiemHetHan=expiration_time,
        MaTK=new_account.MaTK
    )

    db.session.add(new_token)
    db.session.commit()

    user_email = new_account.TenDangNhap

    # After successful registration, send an email
    msg = Message('Welcome!', sender=os.getenv("EMAIL_ADDRESS"), recipients=[user_email])
    msg.body = f'Cảm ơn bạn đã đăng ký. Vui lòng xác minh email của bạn bằng bằng đường dẫn này /verify-email/{token} trên trang của chúng tôi'
    mail.send(msg)

    return jsonify({"message": "Đăng ký thành công! Vui lòng kiểm tra hộp thư của bạn để nhận hướng dẫn xác minh email!"}), 201

@general_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Extract username and password from the request
    username = data.get('email')
    password = data.get('password')

    # Validate parameters
    if not all([username, password]):
        return jsonify({"error": "Xin hãy nhập đủ email và mật khẩu!"}), 400

    # Query the database for the user
    user = db.session.execute(
        db.select(TaiKhoan).where(TaiKhoan.TenDangNhap == username)
    ).scalar_one_or_none()

    # Check if the user exists and verify the password
    if user and bcrypt.checkpw(password.encode('utf-8'), user.MatKhau.encode('utf-8')):
        if user.VaiTro == "user":
            u = db.session.execute(
                db.select(KhachHang).where(KhachHang.MaKH == user.MaKH)
            ).scalar_one_or_none()
            if u.TrangThai == False:
                return jsonify({"error": "Email hoặc mật khẩu không hợp lệ."}), 401
            if user.XacMinhEmail == False:
                return jsonify({"error": "Hãy xác minh email của bạn trước!"}), 401

            cart = db.session.query(GioHang).filter_by(MaKH=user.MaKH).first()

        elif user.VaiTro == "staff":
            u = db.session.execute(
                db.select(NhanVien).where(NhanVien.MaNV == user.MaNV)
            ).scalar_one_or_none()
            if u.TrangThai == False:
                return jsonify({"error": "Tên người dùng hoặc mật khẩu không hợp lệ."}), 401
        
        # Store user session data
        session['user_id'] = user.MaTK
        session['role'] = user.VaiTro
        if user.VaiTro == "user":
            session['cart_id'] = cart.MaGioHang
            session['customer_id'] = user.MaKH

        # Set the session to be permanent and define the lifetime
        session.permanent = True
        #app.permanent_session_lifetime = timedelta(days=3)  # Set session lifetime to 3 days

        return jsonify({"message": "Đăng nhập thành công!", "user_id": user.MaTK, "role": user.VaiTro}), 200
    
    return jsonify({"error": "Tên người dùng hoặc mật khẩu không hợp lệ."}), 401

@general_bp.route('/logout', methods=['POST'])
def logout():
    # Clear the session
    session.pop('user_id', None)
    session.pop('cart_id', None)
    session.pop('role', None)
    session.pop('customer_id', None)
    return jsonify({"message": "Đăng xuất thành công!"}), 200

@general_bp.route('/my-role', methods=['GET'])
def my_role():
    if session:
        if session['role'] == 'admin':
            return jsonify({"role": "admin"}), 200
        elif session['role'] == 'staff':
            return jsonify({"role": "staff"}), 200
        elif session['role'] == 'user':
            return jsonify({"role": "user"}), 200
    return jsonify({"role": "none"}), 200

@general_bp.route('/verify-email/<string:token>', methods=['GET'])
def verify_email(token):
    # Query the Token table for the provided token
    token_entry = db.session.query(Token).filter_by(Token=token).first()

    if not token_entry or token_entry.ThoiDiemHetHan < datetime.now() or token_entry.LoaiToken != "VerifyEmail":
        return jsonify({"error": "Mã token không hợp lệ hoặc đã hết hạn."}), 400

    # Token is valid and not expired; now update email verification status
    account = db.session.query(TaiKhoan).filter_by(MaTK=token_entry.MaTK).first()

    if not account:
        return jsonify({"error": "Không tìm thấy tài khoản"}), 404

    # Set email verification status to True
    account.XacMinhEmail = True
    db.session.commit()

    # Delete the token after successful verification
    db.session.delete(token_entry)
    db.session.commit()

    return jsonify({"message": "Xác minh email thành công!"}), 200

@general_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()

    # Extract the email parameter
    email = data.get('email')

    # Check if the email exists in the TaiKhoan table
    account = db.session.query(TaiKhoan).filter_by(TenDangNhap=email).first()

    if account:
        # Generate a random token
        reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
        expiration_time = datetime.now() + timedelta(minutes=30)

        # Insert into Token table with LoaiToken set to "ResetPassword"
        new_token = Token(
            Token=reset_token,
            LoaiToken="ResetPassword",
            ThoiDiemHetHan=expiration_time,
            MaTK=account.MaTK
        )

        #print(reset_token)

        db.session.add(new_token)
        db.session.commit()

        msg = Message('Yêu cầu đặt lại mật khẩu.', sender=os.getenv("EMAIL_ADDRESS"), recipients=[account.TenDangNhap])
        msg.body = f'Vui lòng truy cập vào đường dẫn này trên trang của chúng tôi để thay đổi mật khẩu của bạn\n /reset-password/{reset_token}'
        mail.send(msg)

    # Always return this message regardless of email existence
    return jsonify({"message": "Chúng tôi đã gửi mã token đặt lại mật khẩu đến email của bạn."}), 200

@general_bp.route('/reset-password/<string:reset_token>', methods=['POST'])
def reset_password(reset_token):
    data = request.get_json()

    # Extract new password parameters
    new_password = data.get('new_password')
    confirm_new_password = data.get('confirm_new_password')

    # Check if the reset token exists
    token_entry = db.session.query(Token).filter_by(Token=reset_token).first()

    if not token_entry or token_entry.ThoiDiemHetHan < datetime.now() or token_entry.LoaiToken != "ResetPassword":
        return jsonify({"error": "Mã token không hợp lệ hoặc đã hết hạn"}), 400

    # Check if new passwords match
    if new_password != confirm_new_password:
        return jsonify({"error": "Mật khẩu không khớp."}), 400

    # Hash the new password
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt(rounds=10)).decode('utf-8')

    # Update the password in the TaiKhoan table
    account = db.session.query(TaiKhoan).filter_by(MaTK=token_entry.MaTK).first()

    if not account:
        return jsonify({"error": "Không tìm thấy tài khoản."}), 404

    account.MatKhau = hashed_password
    db.session.commit()

    # Optionally, delete the token after successful password reset
    db.session.delete(token_entry)
    db.session.commit()

    return jsonify({"message": "Mật khẩu đã được đặt lại thành công!"}), 200

@general_bp.route('/check-reset-password-token/<string:reset_token>', methods=['GET'])
def check_token(reset_token):
    # Check if the reset token exists
    token_entry = db.session.query(Token).filter_by(Token=reset_token).first()

    if not token_entry or token_entry.ThoiDiemHetHan < datetime.now() or token_entry.LoaiToken != "ResetPassword":
        return jsonify({"error": "Invalid or expired token."}), 400
    return jsonify({"message": "Token is valid"}), 200

@general_bp.route('/data/get-products', methods=['GET'])
def get_products():
    # Get optional category_id from query parameters
    category_id = request.args.get('category_id', type=int)
    excluded_product_id = request.args.get('product_id', type=int)

    # Base query to get products
    query = db.session.query(SanPham).filter(SanPham.SoLuong >= 0)  # Filter out products with stock < 1

    # If category_id is provided, filter by category
    if category_id is not None:
        query = query.filter(SanPham.MaDanhMuc == category_id)

    # If excluded_product_id is provided, exclude that product
    if excluded_product_id is not None:
        query = query.filter(SanPham.MaSP != excluded_product_id)

    # Execute the query
    products = query.all()

    # Prepare the response data
    product_list = []
    for p in products:
        category = db.session.query(DanhMuc).filter_by(MaDanhMuc=p.MaDanhMuc).first()
        category_name = category.TenDanhMuc if category else "Unknown"

        product_list.append({
            "product_id": p.MaSP,
            "product_image": p.MaAnh,
            "product_name": p.TenSP,
            "product_description": p.MoTa,
            "product_price": p.GiaBan,
            "product_stock": p.SoLuong,
            "product_category": p.MaDanhMuc,
            "category_name": category_name
            
        })

    return jsonify(product_list), 200

@general_bp.route('/data/get-product/<int:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    # Query to find the product by its ID and check stock quantity
    product = db.session.query(SanPham).filter(SanPham.MaSP == product_id, SanPham.SoLuong >= 0).first()

    if product is None:
        return jsonify({"error": "Product not found or out of stock."}), 404

    # Get the category name
    category = db.session.query(DanhMuc).filter_by(MaDanhMuc=product.MaDanhMuc).first()
    category_name = category.TenDanhMuc if category else "Unknown"

    # Return the product details
    return jsonify({
        "product_id": product.MaSP,
        "product_image": product.MaAnh,
        "product_name": product.TenSP,
        "product_description": product.MoTa,
        "product_price": product.GiaBan,
        "product_stock": product.SoLuong,
        "product_category": product.MaDanhMuc,
        "category_name": category_name
        
    }), 200

@general_bp.route('/data/get-top-products', methods=['GET'])
def get_top_products():
    # Query to get the top 4 products by total quantity sold
    results = db.session.query(
        ChiTietDonHang.MaSP,
        db.func.sum(ChiTietDonHang.SoLuongSP).label('total_sold')
    ).group_by(ChiTietDonHang.MaSP) \
     .order_by(db.func.sum(ChiTietDonHang.SoLuongSP).desc()) \
     .limit(4) \
     .all()

    # Fetch product details for the top selling products
    top_products = []
    for result in results:
        product = db.session.query(SanPham).filter_by(MaSP=result.MaSP).first()
        if product:
            product_data = {
                'product_id': product.MaSP,
                'product_image': product.MaAnh,
                'product_name': product.TenSP,
                'product_description': product.MoTa,
                'product_price': product.GiaBan,
                'product_stock': product.SoLuong,
                'product_category': product.MaDanhMuc
            }
            top_products.append(product_data)

    return jsonify(top_products), 200

@general_bp.route('/data/get-categories', methods=['GET'])
def get_categories():
    categories = db.session.execute(db.select(DanhMuc)).scalars().all()
    return jsonify([{"category_id": c.MaDanhMuc, "category_name": c.TenDanhMuc} for c in categories]), 200

@general_bp.route('/setting/change-personal-data', methods=['POST'])
def change_personal_data():
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"error": "User not authenticated."}), 401

    # Fetch the account record to determine the corresponding user ID
    account = db.session.query(TaiKhoan).filter_by(MaTK=user_id).first()
    
    if not account:
        return jsonify({"error": "Account not found."}), 404

    # Determine which model to update based on the role
    if account.VaiTro == 'user':
        person = db.session.get(KhachHang, account.MaKH)
        if not person:
            return jsonify({"error": "User not found."}), 404
    elif account.VaiTro == 'staff':
        person = db.session.get(NhanVien, account.MaNV)
        if not person:
            return jsonify({"error": "Staff not found."}), 404
    elif account.VaiTro == 'admin':
        person = db.session.get(QuanLy, account.MaQL)
        if not person:
            return jsonify({"error": "Admin not found."}), 404
    else:
        return jsonify({"error": "Invalid role."}), 403

    # Get parameters from the request
    name = request.json.get('name')
    phone = request.json.get('phone')
    email = request.json.get('email')
    birthday = request.json.get('birthday')
    password = request.json.get('password')
    confirm_password = request.json.get('confirm_password')
    status = request.json.get('status')

    # Check password requirements
    if password or confirm_password:
        if not password or not confirm_password:
            return jsonify({"error": "Hãy nhập mật khẩu mới ở cả 2 ô."}), 400
        if password != confirm_password:
            return jsonify({"error": "Mật khẩu mới không khớp."}), 400
        
        # Hash the password
        account.MatKhau = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=10)).decode('utf-8')

    # Update fields based on the role
    if name:
        if account.VaiTro == 'user':
            person.TenKH = name
        elif account.VaiTro == 'staff':
            person.TenNV = name
        elif account.VaiTro == 'admin':
            person.TenQL = name

    if phone:
        person.Sdt = phone

    if email:
        person.Email = email
        account.TenDangNhap = email

    if birthday:
        # Convert birthday from string to date object
        try:
            birthday = datetime.strptime(birthday, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
        person.NgaySinh = birthday

    if status is not None:  # Check if status is provided
        if account.VaiTro in ['staff', 'admin']:
            return jsonify({"error": "Nhân viên và quản lí không thể thay đổi trạng thái của chính mình."}), 403
        person.TrangThai = bool(status)  # Ensure status is boolean

    # Commit the changes to the database
    db.session.commit()

    return jsonify({"message": "Thông tin cá nhân cập nhật thành công."}), 200

@general_bp.route('/data/get-personal-data', methods=['GET'])
def get_personal_data():
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"error": "User not authenticated."}), 401

    # Fetch the account record to determine the corresponding user ID
    account = db.session.query(TaiKhoan).filter_by(MaTK=user_id).first()
    
    if not account:
        return jsonify({"error": "Account not found."}), 404

    # Determine which model to update based on the role
    if account.VaiTro == 'user':
        person = db.session.get(KhachHang, account.MaKH)
        if not person:
            return jsonify({"error": "User not found."}), 404
    elif account.VaiTro == 'staff':
        person = db.session.get(NhanVien, account.MaNV)
        if not person:
            return jsonify({"error": "Staff not found."}), 404
    elif account.VaiTro == 'admin':
        person = db.session.get(QuanLy, account.MaQL)
        if not person:
            return jsonify({"error": "Admin not found."}), 404
    else:
        return jsonify({"error": "Invalid role."}), 403

    # Determine which model to query based on the role
    if role == 'user':
        data = {
            "name": person.TenKH,
            "email": person.Email,
            "birthday": person.NgaySinh.strftime("%Y-%m-%d"),
            "phone": person.Sdt
        }
    elif role == 'staff':
        data = {
            "name": person.TenNV,
            "email": person.Email,
            "birthday": person.NgaySinh.strftime("%Y-%m-%d"),
            "phone": person.Sdt
        }
    elif role == 'admin':
        data = {
            "name": person.TenQL,
            "email": person.Email,
            "birthday": person.NgaySinh.strftime("%Y-%m-%d"),
            "phone": person.Sdt
        }
    else:
        return jsonify({"error": "Invalid role."}), 403

    return jsonify(data), 200

@general_bp.route('/data/get-comment/<int:product_id>', methods=['GET'])
def get_comment(product_id):
    # Check if the product exists
    comments = db.session.query(DanhGia).filter_by(MaSP=product_id).all()

    if not comments:
        return jsonify({"message": "Không có bình luận."}), 200

    comment_list = []

    # Get user ID from the session if it exists
    user_id = session.get('user_id')  # Change to the actual key used for user ID in your session

    # Initialize MaKH to None
    customer_id = None

    # If user_id exists, query TaiKhoan to get MaKH
    if user_id:
        account = db.session.query(TaiKhoan).filter_by(MaTK=user_id).first()
        if account:
            customer_id = account.MaKH

    for comment in comments:
        customer = db.session.query(KhachHang).filter_by(MaKH=comment.MaKH).first()
        customer_name = customer.TenKH if customer else "Unknown"

        # Check if the current user is the owner of the comment
        is_owner = (customer_id == comment.MaKH) if customer_id else False

        comment_list.append({
            "comment_id": comment.MaDanhGia,
            "comment_text": comment.BinhLuan,
            "comment_date": comment.NgayDanhGia.strftime("%Y-%m-%d"),
            "customer_name": customer_name,
            "is_owner": is_owner
        })

    return jsonify(comment_list), 200

@general_bp.route('/data/images/<path:filepath>', methods=['GET'])
def get_image(filepath):
    # Define the uploads directory (adjust the path as necessary)

    # Check if the file exists
    if not os.path.isfile(os.path.join(UPLOAD_FOLDER, filepath)):
        return abort(404)  # Return 404 if the file does not exist

    # Serve the image file
    return send_from_directory(UPLOAD_FOLDER, filepath)