# insert_sample_data.py

from app import create_app, db
from app.models import DonHang, ChiTietDonHang, DanhGia, SanPham, KhachHang, DanhMuc, QuanLy, NhanVien, TaiKhoan  # Import your models
import datetime, uuid, bcrypt, random
from datetime import datetime, timedelta

app = create_app()

start_date = datetime(2024, 3, 1)
end_date = datetime(2025, 3, 31)

with app.app_context():
    # Sample data for DonHang
    # don_hang_samples = [
    #     DonHang(TongTien=150.0, TrangThai='Chờ xử lí', DiaChi='123 Main St', Sdt='123456789', PhuongThucThanhToan='Credit Card', MaKH=1, MaNV=1),
    #     DonHang(TongTien=150.0, TrangThai='Chờ xử lí', DiaChi='123 Main St', Sdt='123456789', PhuongThucThanhToan='Credit Card', MaKH=1, MaNV=1),
    #     DonHang(TongTien=150.0, TrangThai='Chờ xử lí', DiaChi='123 Main St', Sdt='123456789', PhuongThucThanhToan='Credit Card', MaKH=1, MaNV=1),
    #     DonHang(TongTien=150.0, TrangThai='Chờ xử lí', DiaChi='123 Main St', Sdt='123456789', PhuongThucThanhToan='Credit Card', MaKH=1, MaNV=1)
    # ]

    # admin_sample = [
    #     QuanLy(TenQL="test",NgaySinh=datetime.datetime.now(), Email="admin@admin.shop", Sdt='123')
    # ]
    
    # # Sample data for ChiTietDonHang
    # chi_tiet_samples = [
    #     ChiTietDonHang(MaDonHang=1, MaSP=1, SoLuongSP=50, DonGia=75.0),
    #     ChiTietDonHang(MaDonHang=2, MaSP=2, SoLuongSP=100, DonGia=200.0),
    #     ChiTietDonHang(MaDonHang=3, MaSP=3, SoLuongSP=75, DonGia=100.0),
    #     ChiTietDonHang(MaDonHang=4, MaSP=4, SoLuongSP=10, DonGia=100.0),
    #     ChiTietDonHang(MaDonHang=5, MaSP=5, SoLuongSP=25, DonGia=100.0)
    # ]

    # danh_muc_samples = [
    #     DanhMuc(TenDanhMuc="Test1"),
    #     DanhMuc(TenDanhMuc="Test2")
    # ]

    # product_sample = [
    #     SanPham(MaAnh="1/image.png", TenSP="test1", GiaBan=10, SoLuong=10, MaDanhMuc=1),
    #     SanPham(MaAnh="1/image.png", TenSP="test2", GiaBan=10, SoLuong=10, MaDanhMuc=2),
    #     SanPham(MaAnh="1/image.png", TenSP="test3", GiaBan=10, SoLuong=10, MaDanhMuc=3),
    #     SanPham(MaAnh="1/image.png", TenSP="test4", GiaBan=10, SoLuong=10, MaDanhMuc=1),
    #     SanPham(MaAnh="1/image.png", TenSP="test5", GiaBan=10, SoLuong=10, MaDanhMuc=2),
    #     SanPham(MaAnh="1/image.png", TenSP="test6", GiaBan=10, SoLuong=10, MaDanhMuc=3),
    #     SanPham(MaAnh="1/image.png", TenSP="test7", GiaBan=10, SoLuong=10, MaDanhMuc=1),
    #     SanPham(MaAnh="1/image.png", TenSP="test8", GiaBan=10, SoLuong=10, MaDanhMuc=2),
    #     SanPham(MaAnh="1/image.png", TenSP="test9", GiaBan=10, SoLuong=10, MaDanhMuc=3),
    #     SanPham(MaAnh="1/image.png", TenSP="test10", GiaBan=10, SoLuong=10, MaDanhMuc=1),
    #     SanPham(MaAnh="1/image.png", TenSP="test11", GiaBan=10, SoLuong=10, MaDanhMuc=2),
    #     SanPham(MaAnh="1/image.png", TenSP="test12", GiaBan=10, SoLuong=10, MaDanhMuc=3),
    # ]
    
    #Sample data for DanhGia
    # danh_gia_samples = [
    #     DanhGia(BinhLuan='Excellent product!', MaKH=1, MaSP=1),
    #     DanhGia(BinhLuan='Good value for money.', MaKH=2, MaSP=2),
    #     DanhGia(BinhLuan='Not satisfied with the quality.', MaKH=1, MaSP=3)
    # ]

    # Generate 10 staff members
    staff_list = [
        NhanVien(
            TenNV=f"Staff {i}",
            NgaySinh=datetime(1985 + i % 10, i % 12 + 1, i % 28 + 1),
            Email=f"staff{i}@example.com",
            Sdt=f"09{i}5678{i}90",
            TrangThai=True if i % 2 == 0 else False
        )
        for i in range(1, 11)
    ]

    # Generate 10 customers
    customer_list = [
        KhachHang(
            TenKH=f"Customer {i}",
            NgaySinh=datetime(1990 + i % 10, i % 12 + 1, i % 28 + 1),
            Email=f"customer{i}@example.com",
            Sdt=f"08{i}1234{i}56",
            TrangThai=True if i % 2 == 0 else False
        )
        for i in range(1, 11)
    ]

    # Generate 20 user accounts
    user_list = [
        TaiKhoan(
            MaTK=str(uuid.uuid4()),
            TenDangNhap=f"staff{i}@example.com",
            MatKhau=bcrypt.hashpw("123".encode('utf-8'), bcrypt.gensalt(rounds=10)).decode('utf-8'),
            VaiTro="staff",
            MaKH=None,
            MaQL=None,
            MaNV=i,
            XacMinhEmail=True
        )
        for i in range(1, 11)
    ] + [
        TaiKhoan(
            MaTK=str(uuid.uuid4()),
            TenDangNhap=f"customer{i}@example.com",
            MatKhau=bcrypt.hashpw("123".encode('utf-8'), bcrypt.gensalt(rounds=10)).decode('utf-8'),
            VaiTro="user",
            MaKH=i,
            MaQL=None,
            MaNV=None,
            XacMinhEmail=False
        )
        for i in range(1, 11)
    ]

    # Generate 10 random DonHang entries
    # don_hang_samples = [
    #     DonHang(
    #         TongTien=random.uniform(100, 1000),
    #         TrangThai=random.choice(['Đã giao']),
    #         DiaChi=f'{random.randint(1, 999)} Main St',
    #         Sdt=f'09{random.randint(10000000, 99999999)}',
    #         PhuongThucThanhToan=random.choice(['Credit Card', 'Cash', 'Bank Transfer']),
    #         NgayTao=start_date + timedelta(days=random.randint(0, (end_date - start_date).days)),
    #         MaKH=1,
    #         MaNV=1
    #     )
    #     for _ in range(100)
    # ]

    # # Generate 100 random ChiTietDonHang entries
    # chi_tiet_samples = [
    #     ChiTietDonHang(
    #         MaDonHang=i,  # Matches one of the DonHang IDs
    #         MaSP=random.randint(1, 25),       # Product IDs between 1 and 10
    #         SoLuongSP=random.randint(1, 50),  # Random quantity
    #         DonGia=random.uniform(50, 500)    # Random price per unit
    #     )
    #     for i in range(200, 299)
    # ]
    
    #Add and commit DonHang samples
    db.session.bulk_save_objects(customer_list)
    db.session.bulk_save_objects(staff_list)
    db.session.bulk_save_objects(user_list)
    # db.session.commit()
    
    # Add and commit ChiTietDonHang samples
    #b.session.bulk_save_objects(don_hang_samples)
    #db.session.bulk_save_objects(chi_tiet_samples)
    db.session.commit()
    
    # # Add and commit DanhGia samples
    # db.session.bulk_save_objects(danh_gia_samples)
    # db.session.commit()

    # db.session.bulk_save_objects(chi_tiet_samples)
    # db.session.commit()

    # db.session.bulk_save_objects(chi_tiet_samples)
    # db.session.commit()

    print("Sample data inserted successfully.")