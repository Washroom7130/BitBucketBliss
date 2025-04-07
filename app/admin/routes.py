# app/admin/routes.py

from flask import Blueprint, jsonify, request, session, abort
from app.database import db
from app.models import KhachHang, NhanVien, SanPham, DanhMuc, DanhGia, DonHang, ChiTietDonHang, TaiKhoan
from datetime import datetime, timedelta
from sqlalchemy import func
import calendar

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    def wrapper(*args, **kwargs):
        #if session: print('Yes')
        if 'role' not in session or session['role'] != 'admin':
            return jsonify({"error": "Access denied. Admins only."}), 403
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__  # Preserve function name for Flask
    return wrapper

def admin_or_staff_required(f):
    def wrapper(*args, **kwargs):
        if 'role' not in session or session['role'] not in ['admin', 'staff']:
            return jsonify({"error": "Access denied. Admins and staff only."}), 403
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__  # Preserve function name for Flask
    return wrapper

@admin_bp.route('/admin/get-users', methods=['GET'])
@admin_required  # Apply the decorator to the route
def get_users():
    users = db.session.execute(db.select(TaiKhoan)).scalars().all()
    return jsonify([{"user_id": user.MaTK, "username": user.TenDangNhap, "role": user.VaiTro} for user in users]), 200

@admin_bp.route('/staff/get-customers', methods=['GET'])
@admin_or_staff_required  # Apply the decorator to the route
def get_customers():
    customers = db.session.execute(db.select(KhachHang)).scalars().all()
    result = []
    for customer in customers:
        # If customer.NgaySinh is a datetime object, format it as "05 Apr 2000"
        birthday = customer.NgaySinh.strftime('%d %b %Y')
        

        # Map the boolean status to text
        status_text = "Active" if customer.TrangThai else "Inactive"

        result.append({
            "customer_id": customer.MaKH,
            "customer_name": customer.TenKH,
            "customer_birthday": birthday,
            "customer_email": customer.Email,
            "customer_phone_num": customer.Sdt,
            "customer_status": status_text
        })

    return jsonify(result), 200

@admin_bp.route('/admin/get-staff', methods=['GET'])
@admin_required  # Apply the decorator to the route
def get_staff():
    staff = db.session.execute(db.select(NhanVien)).scalars().all()
    result = []
    for s in staff:
        # If customer.NgaySinh is a datetime object, format it as "05 Apr 2000"
        birthday = s.NgaySinh.strftime('%d %b %Y')
        

        # Map the boolean status to text
        status_text = "Active" if s.TrangThai else "Inactive"

        result.append({
            "staff_id": s.MaNV,
            "staff_name": s.TenNV,
            "staff_birthday": birthday,
            "staff_email": s.Email,
            "staff_phone_num": s.Sdt,
            "staff_status": status_text
        })

    return jsonify(result), 200

@admin_bp.route('/staff/get-comments', methods=['GET'])
@admin_or_staff_required  # Apply the decorator to the route
def get_comments():
    comments = db.session.execute(db.select(DanhGia)).scalars().all()
    return jsonify([{"comment_id": co.MaDanhGia, "comment_value": co.BinhLuan, "comment_date": co.NgayDanhGia, "customer_id": co.MaKH, "product_id": co.MaSP} for co in comments]), 200

@admin_bp.route('/staff/get-orders', methods=['GET'])
@admin_or_staff_required  # Apply the decorator to the route
def get_orders():
    orders = db.session.execute(db.select(DonHang)).scalars().all()
    return jsonify([{"order_id": o.MaDonHang, "creation_date": o.NgayTao, "total": o.TongTien, "order_status": o.TrangThai, "delivery_address": o.DiaChi, "customer_phone_number": o.Sdt, "order_payment_type": o.PhuongThucThanhToan, "customer_id": o.MaKH, "staff_id": o.MaNV} for o in orders]), 200

@admin_bp.route('/staff/get-order-detail', methods=['GET'])
@admin_or_staff_required  # Apply the decorator to the route
def get_order_detail():
    detail = db.session.execute(db.select(ChiTietDonHang)).scalars().all()
    return jsonify([{"order_id": d.MaDonHang, "product_id": d.MaSP, "total": d.SoLuongSP, "cost_per_piece": d.DonGia} for d in detail]), 200

@admin_bp.route('/admin/get-account-statistics', methods=['GET'])
@admin_required
def get_account_statistics():
    # Total accounts
    total_accounts = db.session.query(TaiKhoan).count()

    # Total staff accounts
    staff_accounts = db.session.query(TaiKhoan).filter(TaiKhoan.MaNV.isnot(None)).all()
    total_staff = len(staff_accounts)

    # Calculate active and inactive staff accounts
    active_staff_count = sum(1 for staff in staff_accounts if staff.MaNV and db.session.query(NhanVien.TrangThai).filter_by(MaNV=staff.MaNV).first()[0])
    inactive_staff_count = total_staff - active_staff_count

    # Total customer accounts
    customer_accounts = db.session.query(TaiKhoan).filter(TaiKhoan.MaKH.isnot(None)).all()
    total_customers = len(customer_accounts)

    # Calculate active and non-verified customer accounts
    active_customer_count = sum(1 for customer in customer_accounts if customer.MaKH and db.session.query(KhachHang.TrangThai).filter_by(MaKH=customer.MaKH).first()[0] and customer.XacMinhEmail)
    non_verified_customer_count = sum(1 for customer in customer_accounts if customer.MaKH and db.session.query(KhachHang.TrangThai).filter_by(MaKH=customer.MaKH).first()[0] and not customer.XacMinhEmail)
    inactive_customer_count = total_customers - (active_customer_count + non_verified_customer_count)

    # Prepare the response data with total counts
    statistics = {
        "active_staff_count": active_staff_count,
        "inactive_staff_count": inactive_staff_count,
        "active_customer_count": active_customer_count,
        "non_verified_customer_count": non_verified_customer_count,
        "inactive_customer_count": inactive_customer_count
    }

    return jsonify(statistics), 200

@admin_bp.route('/admin/get-category-marketshare', methods=['GET'])
@admin_required
def get_category_marketshare():
    # Query ChiTietDonHang to get total quantity of all orders
    total_orders = db.session.query(db.func.sum(ChiTietDonHang.SoLuongSP)).scalar() or 0

    # Get all categories
    categories = db.session.query(DanhMuc).all()
    
    # Create a dictionary to hold sales data
    category_sales = {category.TenDanhMuc: 0 for category in categories}

    if total_orders == 0:
        # Populate categories with 0 if no orders exist
        result = [{"TenDanhMuc": category, "TotalQuantity": 0} for category in category_sales.keys()]
        return jsonify(result), 200

    # Query to get the count of products ordered by MaSP
    product_orders = db.session.query(
        ChiTietDonHang.MaSP,
        db.func.sum(ChiTietDonHang.SoLuongSP).label('total_quantity')
    ).group_by(ChiTietDonHang.MaSP).all()

    for product_order in product_orders:
        product_id = product_order.MaSP
        quantity = product_order.total_quantity

        # Get category for the product
        product = db.session.query(SanPham).filter_by(MaSP=product_id).first()
        if product:
            category_id = product.MaDanhMuc
            category = db.session.query(DanhMuc).filter_by(MaDanhMuc=category_id).first()

            if category:
                category_name = category.TenDanhMuc
                category_sales[category_name] += quantity

    # Prepare the response data
    result = [{"TenDanhMuc": category, "TotalQuantity": quantity} for category, quantity in category_sales.items()]

    return jsonify(result), 200

@admin_bp.route('/admin/get-order-statistics', methods=['GET'])
@admin_required
def get_order_statistics():
    # Initialize counts for each status
    order_stats = {
        "Chờ xử lí": 0,
        "Xác nhận": 0,
        "Đang giao": 0,
        "Đã giao": 0,
        "Đã hủy": 0
    }

    # Query the DonHang table for each status
    for status in order_stats.keys():
        count = db.session.query(DonHang).filter_by(TrangThai=status).count()
        order_stats[status] = count

    return jsonify(order_stats), 200

@admin_bp.route('/admin/get-annual-earning', methods=['GET'])
@admin_required
def get_annual_earning():
    today = datetime.now()
    monthly_earnings = []
    
    # Loop over the last 12 months
    for i in range(12):
        # Calculate the correct year and month for i months ago
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1

        # The first day of the month
        start_date = datetime(year, month, 1)
        # The first day of the next month
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Query for total earnings in the month
        total_earning = db.session.query(func.sum(DonHang.TongTien)).filter(
            DonHang.TrangThai == "Đã giao",
            DonHang.NgayTao >= start_date,
            DonHang.NgayTao < end_date
        ).scalar() or 0

        monthly_earnings.append({
            "month": start_date.strftime("%Y-%m"),
            "total_earning": total_earning
        })

    return jsonify(monthly_earnings), 200

