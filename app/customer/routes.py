# customer/routes.py

from flask import Blueprint, jsonify, request, session, abort
from app.database import db
from app.models import KhachHang, SanPham, DanhMuc, DanhGia, DonHang, ChiTietDonHang, TaiKhoan, GioHang, ChiTietGioHang

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/customer/get-cart', methods=['GET'])
def get_cart():
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({"error": "User not authenticated."}), 401

    cart_id = session.get('cart_id')

    # Fetch cart details with product names and prices
    cart_items = db.session.query(
        ChiTietGioHang,
        SanPham.TenSP,
        SanPham.GiaBan,
        SanPham.MaAnh
    ).join(SanPham, ChiTietGioHang.MaSP == SanPham.MaSP).filter(ChiTietGioHang.MaGioHang == cart_id, ChiTietGioHang.SoLuong != 0).all()
    
    # Prepare the response data
    items = []
    for item, product_name, price, product_image in cart_items:
        total_cost = item.SoLuong * price  # Calculate total cost
        items.append({
            "MaSP": item.MaSP,
            "TenSP": product_name,  # Include product name
            "MaAnh": product_image,
            "SoLuong": item.SoLuong,
            "TotalCost": total_cost  # Include total cost
        })

    return jsonify({"MaGioHang": cart_id, "items": items}), 200

@customer_bp.route('/customer/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    user_id = session.get('user_id')
    cart_id = session.get('cart_id')

    if not user_id:
        return jsonify({"error": "User not authenticated."}), 401

    if not cart_id:
        return jsonify({"error": "Staff and admin can't use this function"}), 401

    # Check if the product exists
    product = db.session.query(SanPham).filter_by(MaSP=product_id).first()

    if not product:
        return jsonify({"error": "Product not found."}), 404

    # Get the quantity from the request
    quantity = request.json.get('quantity')

    if not isinstance(quantity, int) or quantity <= 0 or quantity > product.SoLuong:
        return jsonify({"error": "Quantity must be a positive integer and not larger than stock."}), 400

    # Fetch or create the cart for the user
    cart = db.session.query(GioHang).filter_by(MaGioHang=cart_id).first()

    # Check if the item already exists in the cart
    cart_item = db.session.query(ChiTietGioHang).filter_by(MaGioHang=cart_id, MaSP=product_id).first()

    if cart_item:
        # Update the quantity if the item already exists
        cart_item.SoLuong += quantity
    else:
        # Add new item to the cart
        cart_item = ChiTietGioHang(MaGioHang=cart.MaGioHang, MaSP=product_id, SoLuong=quantity)
        db.session.add(cart_item)

    product.SoLuong -= quantity

    # Commit the changes to the database
    db.session.commit()

    return jsonify({"message": "Thêm sản phẩm vào giỏ hàng thành công."}), 200

@customer_bp.route('/customer/change-item-quantity/<int:product_id>', methods=['POST'])
def change_item_quantity(product_id):
    user_id = session.get('user_id')
    cart_id = session.get('cart_id')

    if not user_id:
        return jsonify({"error": "User not authenticated."}), 401

    cart_item = db.session.query(ChiTietGioHang).filter_by(MaGioHang=cart_id, MaSP=product_id).first()

    if not cart_item:
        return jsonify({"error": "Item not found in cart."}), 404

    # Check if the product exists
    product = db.session.query(SanPham).filter_by(MaSP=product_id).first()

    if not product:
        return jsonify({"error": "Product not found."}), 404

    # Get the new quantity from the request
    quantity = request.json.get('quantity')

    if not isinstance(quantity, int) or quantity < 0:
        return jsonify({"error": "Quantity must be a non-negative integer."}), 400

    if quantity == 0:
        # Remove the item from the cart
        product.SoLuong += cart_item.SoLuong
        db.session.delete(cart_item)
    else:
        # Update the quantity of the item in the cart
        cart_item.SoLuong = quantity

    # Commit the changes to the database
    db.session.commit()

    return jsonify({"message": "Item quantity updated successfully."}), 200

@customer_bp.route('/customer/place-order', methods=['POST'])
def place_order():
    user_id = session.get('user_id')
    cart_id = session.get('cart_id')
    ma_kh = session.get('customer_id')

    if not user_id:
        return jsonify({"error": "User not authenticated."}), 401

    # Check if the cart exists
    cart = db.session.query(GioHang).filter_by(MaGioHang=cart_id, MaKH=ma_kh).first()
    
    if not cart:
        return jsonify({"error": "Cart not found or does not belong to user."}), 404

    # Check if the cart is empty
    cart_items = db.session.query(ChiTietGioHang).filter_by(MaGioHang=cart_id).all()

    if not cart_items:
        return jsonify({"error": "Cart is empty."}), 400

    # Get address and phone from the request
    address = request.json.get('address')
    phone = request.json.get('phone')

    if not address or not phone:
        return jsonify({"error": "Xin hãy nhập số điện thoại và địa chỉ."}), 400

    total_amount = 0.0
    order_details = []
    
    for item in cart_items:
        product = db.session.query(SanPham).filter_by(MaSP=item.MaSP).first()

        if not product:
            return jsonify({"error": f"Product with ID {item.MaSP} not found."}), 404

        # Calculate total price
        total_price = product.GiaBan * item.SoLuong
        total_amount += total_price

        # Prepare order detail
        order_details.append({
            "MaSP": item.MaSP,
            "SoLuongSP": item.SoLuong,
            "DonGia": product.GiaBan
        })

    # Create a new DonHang object
    new_order = DonHang(
        MaKH=ma_kh,
        MaNV=1,  # Default as provided
        TongTien=total_amount,
        DiaChi=address,
        Sdt=phone
    )

    # Add the order to the session
    db.session.add(new_order)
    db.session.commit()  # Commit to get MaDonHang

    # Create ChiTietDonHang entries
    for detail in order_details:
        order_detail = ChiTietDonHang(
            MaDonHang=new_order.MaDonHang,
            MaSP=detail["MaSP"],
            SoLuongSP=detail["SoLuongSP"],
            DonGia=detail["DonGia"]
        )
        db.session.add(order_detail)

    # Commit the order details to the database
    db.session.commit()

    # Clear the cart
    db.session.query(ChiTietGioHang).filter_by(MaGioHang=cart_id).delete()
    db.session.commit()

    return jsonify({"message": "Đặt hàng thành công!", "MaDonHang": new_order.MaDonHang}), 201

@customer_bp.route('/customer/get-order-detail', methods=['GET'])
def get_order_detail():
    user_id = session.get('user_id')
    ma_kh = session.get('customer_id')

    if not user_id:
        return jsonify({"error": "User not authenticated."}), 401

    # Query all orders for the customer
    orders = db.session.query(DonHang).filter_by(MaKH=ma_kh).all()

    if not orders:
        return jsonify({"message": "No orders found for this customer."}), 200

    order_details = []

    for order in orders:
        # Get order details
        order_info = {
            "MaDonHang": order.MaDonHang,
            "NgayTao": order.NgayTao.strftime("%Y-%m-%d"),
            "TongTien": order.TongTien,
            "TrangThai": order.TrangThai,
            # "Sdt": order.Sdt,
            # "DiaChi": order.DiaChi,
            "items": []
        }

        # Get order items
        order_items = db.session.query(ChiTietDonHang).filter_by(MaDonHang=order.MaDonHang).all()

        for item in order_items:
            product = db.session.query(SanPham).filter_by(MaSP=item.MaSP).first()
            if product:
                order_info["items"].append({
                    "TenSP": product.TenSP,
                    "SoLuong": item.SoLuongSP
                })

        order_details.append(order_info)

    return jsonify(order_details), 200

@customer_bp.route('/customer/update-order-status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    user_id = session.get('user_id')
    ma_kh = session.get('customer_id')

    if not user_id:
        return jsonify({"error": "User not authenticated."}), 401

    # Check if the order exists and belongs to the customer
    order = db.session.query(DonHang).filter_by(MaDonHang=order_id, MaKH=ma_kh).first()
    if not order:
        return jsonify({"error": "Order not found or does not belong to user."}), 404

    # Get the status from the request
    status = request.json.get('status')
    if status != "Đã hủy":
        return jsonify({"error": "Invalid status value. Only 'Đã hủy' is accepted."}), 400

    # Update the order status
    order.TrangThai = status

    # If the order is canceled, add back the product quantities
    order_details = ChiTietDonHang.query.filter_by(MaDonHang=order_id).all()
    for detail in order_details:
        product = db.session.query(SanPham).filter_by(MaSP=detail.MaSP).first()
        if product:
            product.SoLuong += detail.SoLuongSP

    db.session.commit()

    return jsonify({"message": "Order status updated successfully."}), 200

@customer_bp.route('/customer/comment/<int:product_id>', methods=['POST'])
def comment(product_id):
    user_id = session.get('user_id')
    ma_kh = session.get('customer_id')

    if not user_id:
        return jsonify({"error": "User not authenticated."}), 401

    # Check if the product exists
    product = db.session.query(SanPham).filter_by(MaSP=product_id).first()

    if not product:
        return jsonify({"error": "Product not found."}), 404

    # Get the comment from the request
    comment_text = request.json.get('comment')

    if not comment_text:
        return jsonify({"error": "Comment cannot be empty."}), 400

    # Create a new comment
    new_comment = DanhGia(
        BinhLuan=comment_text,
        MaKH=ma_kh,
        MaSP=product_id
    )

    # Add the comment to the session and commit
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({"message": "Comment added successfully."}), 201

@customer_bp.route('/customer/comment/remove-comment/<int:comment_id>', methods=['DELETE'])
def remove_comment(comment_id):
    user_id = session.get('user_id')
    ma_kh = session.get('customer_id')

    if not user_id:
        return jsonify({"error": "User not authenticated."}), 401

    # Check if the comment exists and belongs to the customer
    comment = db.session.query(DanhGia).filter_by(MaDanhGia=comment_id, MaKH=ma_kh).first()

    if not comment:
        return jsonify({"error": "Comment not found or does not belong to user."}), 404

    # Delete the comment
    db.session.delete(comment)
    db.session.commit()

    return jsonify({"message": "Comment removed successfully."}), 200

