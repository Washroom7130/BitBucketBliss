# app/initialize_db.py

from app import db, create_app
from app.models import TaiKhoan, QuanLy, NhanVien, KhachHang, DanhMuc, SanPham, GioHang, ChiTietDonHang, DonHang
import bcrypt, uuid, sqlite3, datetime, random
from datetime import datetime, timedelta

start_date = datetime(2024, 3, 1)
end_date = datetime(2025, 3, 31)

def init_db():
    app = create_app()
    with app.app_context():
        # Drop all tables (if needed)
        db.drop_all()
        db.create_all()
        # with open('setup.sql', 'r') as f:
        #     sql_script = f.read()
        # # Connect to SQLite database
        # conn = sqlite3.connect('dothucong.db')
        # cursor = conn.cursor()
        # cursor.executescript(sql_script)  # Execute the SQL script
        # conn.commit()
        # conn.close()
        print("Database initialized successfully.")

def add_data():
    # Define admin account details
    # admin_username = "admin"
    # admin_password = "AdminDefaultPassPleaseChange123"
    #hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt(rounds=10)).decode('utf-8')
    # admin_role = "admin"

    # # Create the admin account with UUID for MaTK and MaQL set to 1
    # admin_account = TaiKhoan(
    #     MaTK=str(uuid.uuid4()),  # Generate a new UUID
    #     TenDangNhap=admin_username,
    #     MatKhau=hashed_password,
    #     VaiTro=admin_role,
    #     MaKH=None,
    #     MaQL=1,  # Set MaQL to 1
    #     MaNV=None
    # )

    user_list = [
        TaiKhoan(MaTK=str(uuid.uuid4()), TenDangNhap="admin@admin.shop", MatKhau=bcrypt.hashpw("AdminPassword".encode('utf-8'), bcrypt.gensalt(rounds=10)).decode('utf-8'), VaiTro="admin", MaKH=None, MaQL=1, MaNV=None, XacMinhEmail=True),
        TaiKhoan(MaTK=str(uuid.uuid4()), TenDangNhap="lehoangc@example.com", MatKhau=bcrypt.hashpw("123".encode('utf-8'), bcrypt.gensalt(rounds=10)).decode('utf-8'), VaiTro="staff", MaKH=None, MaQL=None, MaNV=1, XacMinhEmail=True),
        TaiKhoan(MaTK=str(uuid.uuid4()), TenDangNhap="phamminhd@example.com", MatKhau=bcrypt.hashpw("123".encode('utf-8'), bcrypt.gensalt(rounds=10)).decode('utf-8'), VaiTro="staff", MaKH=None, MaQL=None, MaNV=2, XacMinhEmail=True),
        TaiKhoan(MaTK=str(uuid.uuid4()), TenDangNhap="dothanhe@example.com", MatKhau=bcrypt.hashpw("123".encode('utf-8'), bcrypt.gensalt(rounds=10)).decode('utf-8'), VaiTro="user", MaKH=1, MaQL=None, MaNV=None, XacMinhEmail=True),
        TaiKhoan(MaTK=str(uuid.uuid4()), TenDangNhap="buithif@example.com", MatKhau=bcrypt.hashpw("123".encode('utf-8'), bcrypt.gensalt(rounds=10)).decode('utf-8'), VaiTro="user", MaKH=2, MaQL=None, MaNV=None, XacMinhEmail=True)
    ]

    admin_list = [
        QuanLy(TenQL='Nguyễn Văn A', NgaySinh=datetime(1985, 5, 20), Email='nguyenvana@example.com', Sdt='0912345678', TrangThai=True)
    ]

    staff_list = [
        NhanVien(TenNV='Lê Hoàng C', NgaySinh=datetime(1995, 10, 10), Email='lehoangc@example.com', Sdt='0934567890', TrangThai=True),
        NhanVien(TenNV='Phạm Minh D', NgaySinh=datetime(1998, 12, 25), Email='phamminhd@example.com', Sdt='0971234567', TrangThai=True)
    ]

    customer_list = [
        KhachHang(TenKH='Đỗ Thanh E', NgaySinh=datetime(2000, 4, 5), Email='dothanhe@example.com', Sdt='0967891234', TrangThai=True),
        KhachHang(TenKH='Bùi Thị F', NgaySinh=datetime(2002, 7, 14), Email='buithif@example.com', Sdt='0956789123', TrangThai=True)
    ]

    category_list = [
        DanhMuc(TenDanhMuc='Gốm sứ'),
        DanhMuc(TenDanhMuc='Tranh nghệ thuật'),
        DanhMuc(TenDanhMuc='Đồ mây tre đan'),
        DanhMuc(TenDanhMuc='Tượng điêu khắc'),
        DanhMuc(TenDanhMuc='Trang sức')
    ]

    product_list = [
        SanPham(MaAnh='1/binh_gom_battrang.jpg', TenSP='Bình gốm Bát Tràng', MoTa='Bình gốm trang trí, họa tiết hoa văn', GiaBan=500000, SoLuong=20, MaDanhMuc=1),
        SanPham(MaAnh='2/bo_am_tra_su.jpg', TenSP='Bộ ấm trà sứ', MoTa='Bộ ấm trà gốm sứ, phong cách cổ điển', GiaBan=750000, SoLuong=20, MaDanhMuc=1),
        SanPham(MaAnh='3/lo_hoa_gom_men_ran.jpg', TenSP='Lọ hoa gốm men rạn', MoTa='Lọ hoa thủ công men rạn, phong cách vintage', GiaBan=600000, SoLuong=20, MaDanhMuc=1),
        SanPham(MaAnh='4/den_ngu_gom.jpg', TenSP='Đèn ngủ gốm', MoTa='Đèn ngủ bằng gốm, chạm khắc tinh xảo', GiaBan=900000, SoLuong=20, MaDanhMuc=1),
        SanPham(MaAnh='5/bat_dia_gom.jpg', TenSP='Bát đĩa gốm', MoTa='Bộ bát đĩa sứ thủ công', GiaBan=850000, SoLuong=20, MaDanhMuc=1),
        SanPham(MaAnh='6/tranh_son_dau.jpg', TenSP='Tranh sơn dầu', MoTa='Tranh canvas treo tường ,tối giản, hiện đại, trang trí nhà đẹp mắt', GiaBan=1200000, SoLuong=20, MaDanhMuc=2),
        SanPham(MaAnh='7/tranh_go_khac.jpg', TenSP='Tranh gỗ khắc', MoTa='Tranh gỗ chạm khắc nghệ thuật', GiaBan=1500000, SoLuong=20, MaDanhMuc=2),
        SanPham(MaAnh='8/tranh_da_quy.jpg', TenSP='Tranh đá quý', MoTa='Tranh phong thủy làm từ đá quý tự nhiên', GiaBan=2000000, SoLuong=20, MaDanhMuc=2),
        SanPham(MaAnh='9/tranh_theu_tay.jpg', TenSP='Tranh thêu tay', MoTa='Tranh thêu phong cảnh, nghệ thuật truyền thống', GiaBan=1100000, SoLuong=20, MaDanhMuc=2),
        SanPham(MaAnh='10/tranh_moc_ban.jpg', TenSP='Tranh mộc bản', MoTa='Tranh in mộc bản cổ điển', GiaBan=900000, SoLuong=20, MaDanhMuc=2),
        SanPham(MaAnh='11/gio_may_dung_do.jpg', TenSP='Giỏ mây đựng đồ', MoTa='Giỏ mây thủ công, dùng đựng vật dụng', GiaBan=300000, SoLuong=20, MaDanhMuc=3),
        SanPham(MaAnh='12/tham_tre_dan.jpg', TenSP='Thảm tre đan', MoTa='Thảm đan từ tre nứa, bền và đẹp', GiaBan=400000, SoLuong=20, MaDanhMuc=3),
        SanPham(MaAnh='13/khay_may_tron.jpg', TenSP='Khay mây tròn', MoTa='Khay mây tròn, thích hợp đựng đồ ăn, trà', GiaBan=350000, SoLuong=20, MaDanhMuc=3),
        SanPham(MaAnh='14/long_den_tre.jpg', TenSP='Lồng đèn tre', MoTa='Lồng đèn thủ công bằng tre', GiaBan=500000, SoLuong=20, MaDanhMuc=3),
        SanPham(MaAnh='15/chau_cay_may.jpg', TenSP='Chậu cây mây', MoTa='Chậu cây handmade từ mây, trang trí nội thất', GiaBan=450000, SoLuong=20, MaDanhMuc=3),
        SanPham(MaAnh='16/tuong_go_phat.jpg', TenSP='Tượng gỗ Phật', MoTa='Tượng gỗ điêu khắc thủ công', GiaBan=2500000, SoLuong=20, MaDanhMuc=4),
        SanPham(MaAnh='17/tuong_da_su_tu.jpg', TenSP='Tượng đá sư tử', MoTa='Tượng đá mỹ nghệ hình sư tử', GiaBan=1800000, SoLuong=20, MaDanhMuc=4),
        SanPham(MaAnh='18/tuong_dong_phong_thuy.jpg', TenSP='Tượng đồng phong thủy', MoTa='Tượng đồng chạm khắc tinh xảo', GiaBan=2200000, SoLuong=20, MaDanhMuc=4),
        SanPham(MaAnh='19/tuong_go_quan_cong.jpg', TenSP='Tượng gỗ Quan Công', MoTa='Tượng Quan Công gỗ hương, điêu khắc tinh xảo', GiaBan=2800000, SoLuong=20, MaDanhMuc=4),
        SanPham(MaAnh='20/tuong_da_ngoc_bich.jpg', TenSP='Tượng đá ngọc bích', MoTa='Tượng điêu khắc từ đá ngọc bích tự nhiên', GiaBan=3200000, SoLuong=20, MaDanhMuc=4),
        SanPham(MaAnh='21/vong_tay_da.jpg', TenSP='Vòng tay đá', MoTa='Vòng tay handmade từ đá tự nhiên', GiaBan=450000, SoLuong=20, MaDanhMuc=5),
        SanPham(MaAnh='22/day_chuyen_bac.jpg', TenSP='Dây chuyền bạc handmade', MoTa='Dây chuyền bạc chế tác thủ công', GiaBan=800000, SoLuong=20, MaDanhMuc=5),
        SanPham(MaAnh='23/nhan_go_phong_thuy.jpg', TenSP='Nhẫn gỗ phong thủy', MoTa='Nhẫn gỗ tự nhiên, khắc hoa văn tinh xảo', GiaBan=500000, SoLuong=20, MaDanhMuc=5),
        SanPham(MaAnh='24/khuyen_tai_handmade.jpg', TenSP='Khuyên tai handmade', MoTa='Khuyên tai đính đá, làm thủ công tinh tế', GiaBan=350000, SoLuong=20, MaDanhMuc=5),
        SanPham(MaAnh='25/lac_tay_bac.jpg', TenSP='Lắc tay bạc', MoTa='Lắc tay bạc kết hợp đá quý, handmade', GiaBan=900000, SoLuong=20, MaDanhMuc=5)
    ]

    cart_list = [
        GioHang(MaGioHang='1', MaKH=1),
        GioHang(MaGioHang='2', MaKH=2)
    ]

    chi_tiet_samples = [
        ChiTietDonHang(MaDonHang=1000001, MaSP=1, SoLuongSP=50, DonGia=75.0),
        ChiTietDonHang(MaDonHang=1000002, MaSP=6, SoLuongSP=100, DonGia=200.0),
        ChiTietDonHang(MaDonHang=1000003, MaSP=11, SoLuongSP=75, DonGia=100.0),
        ChiTietDonHang(MaDonHang=1000004, MaSP=16, SoLuongSP=10, DonGia=100.0),
        ChiTietDonHang(MaDonHang=1000005, MaSP=21, SoLuongSP=25, DonGia=100.0)
    ]

    don_hang_samples = [
        DonHang(
            TongTien=random.uniform(100, 1000),
            TrangThai=random.choice(['Đã giao']),
            DiaChi=f'{random.randint(1, 999)} Main St',
            Sdt=f'09{random.randint(10000000, 99999999)}',
            PhuongThucThanhToan=random.choice(['Khi nhận hàng']),
            NgayTao=start_date + timedelta(days=random.randint(0, (end_date - start_date).days)),
            MaKH=1,
            MaNV=1
        )
        for _ in range(20)
    ] + [
        DonHang(
            TongTien=random.uniform(100, 1000),
            TrangThai=random.choice(['Chờ xử lí', 'Xác nhận', 'Đang giao']),
            DiaChi=f'{random.randint(1, 999)} Main St',
            Sdt=f'09{random.randint(10000000, 99999999)}',
            PhuongThucThanhToan=random.choice(['Khi nhận hàng']),
            NgayTao=start_date + timedelta(days=random.randint(0, (end_date - start_date).days)),
            MaKH=1,
            MaNV=1
        )
        for _ in range(20)
    ]

    # Add the admin account to the session and commit
    # db.session.add(admin_account)
    # db.session.commit()
    # print("Admin account created successfully.")

    db.session.bulk_save_objects(user_list)
    db.session.bulk_save_objects(admin_list)
    db.session.bulk_save_objects(staff_list)
    db.session.bulk_save_objects(customer_list)
    db.session.bulk_save_objects(category_list)
    db.session.bulk_save_objects(product_list)
    db.session.bulk_save_objects(cart_list)
    db.session.bulk_save_objects(chi_tiet_samples)
    db.session.bulk_save_objects(don_hang_samples)

    db.session.commit()
    print("Data created successfully")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        init_db()  # Initialize the database and create tables
        add_data()  # Add the admin account