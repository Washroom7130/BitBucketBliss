from app.database import db  # Import db from database.py
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

class QuanLy(db.Model):
    __tablename__ = 'QuanLy'
    
    MaQL = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenQL = db.Column(db.String, nullable=False)
    NgaySinh = db.Column(db.Date, nullable=False)
    Email = db.Column(db.String, unique=True, nullable=False)
    Sdt = db.Column(db.String, nullable=False)
    TrangThai = db.Column(db.Boolean, default=True)

class NhanVien(db.Model):
    __tablename__ = 'NhanVien'
    
    MaNV = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenNV = db.Column(db.String, nullable=False)
    NgaySinh = db.Column(db.Date, nullable=False)
    Email = db.Column(db.String, unique=True, nullable=False)
    Sdt = db.Column(db.String, nullable=False)
    TrangThai = db.Column(db.Boolean, default=True)

class KhachHang(db.Model):
    __tablename__ = 'KhachHang'
    
    MaKH = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenKH = db.Column(db.String, nullable=False)
    NgaySinh = db.Column(db.Date, nullable=False)
    Email = db.Column(db.String, unique=True, nullable=False)
    Sdt = db.Column(db.String, nullable=False)
    TrangThai = db.Column(db.Boolean, default=True)

class TaiKhoan(db.Model):
    __tablename__ = 'TaiKhoan'
    
    MaTK = db.Column(db.String, primary_key=True)
    TenDangNhap = db.Column(db.String, unique=True, nullable=False)
    MatKhau = db.Column(db.String, nullable=False)
    VaiTro = db.Column(db.String, nullable=False)
    XacMinhEmail = db.Column(db.Boolean, default=False)
    MaKH = db.Column(db.Integer, db.ForeignKey('KhachHang.MaKH'))
    MaQL = db.Column(db.Integer, db.ForeignKey('QuanLy.MaQL'))
    MaNV = db.Column(db.Integer, db.ForeignKey('NhanVien.MaNV'))

class DanhMuc(db.Model):
    __tablename__ = 'DanhMuc'
    
    MaDanhMuc = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenDanhMuc = db.Column(db.String, nullable=False)

class SanPham(db.Model):
    __tablename__ = 'SanPham'
    
    MaSP = db.Column(db.Integer, primary_key=True, autoincrement=True)
    MaAnh = db.Column(db.String)
    TenSP = db.Column(db.String, nullable=False)
    MoTa = db.Column(db.String)
    GiaBan = db.Column(db.Float, nullable=False)
    SoLuong = db.Column(db.Integer, nullable=False)
    MaDanhMuc = db.Column(db.Integer, db.ForeignKey('DanhMuc.MaDanhMuc'))

class DonHang(db.Model):
    __tablename__ = 'DonHang'
    
    MaDonHang = db.Column(db.Integer, primary_key=True, autoincrement=True)
    NgayTao = db.Column(db.DateTime, default=db.func.current_timestamp())
    TongTien = db.Column(db.Float, nullable=False)
    TrangThai = db.Column(db.String, nullable=False, default="Chờ xử lí")
    DiaChi = db.Column(db.String, nullable=False)
    Sdt = db.Column(db.String, nullable=False)
    PhuongThucThanhToan = db.Column(db.String, nullable=False, default="Khi nhận hàng")
    MaKH = db.Column(db.Integer, db.ForeignKey('KhachHang.MaKH'))
    MaNV = db.Column(db.Integer, db.ForeignKey('NhanVien.MaNV'))

class DanhGia(db.Model):
    __tablename__ = 'DanhGia'
    
    MaDanhGia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    BinhLuan = db.Column(db.String)
    NgayDanhGia = db.Column(db.DateTime, default=db.func.current_timestamp())
    MaKH = db.Column(db.Integer, db.ForeignKey('KhachHang.MaKH'))
    MaSP = db.Column(db.Integer, db.ForeignKey('SanPham.MaSP'))

class ChiTietDonHang(db.Model):
    __tablename__ = 'ChiTietDonHang'
    
    MaDonHang = db.Column(db.Integer, db.ForeignKey('DonHang.MaDonHang'), primary_key=True)
    MaSP = db.Column(db.Integer, db.ForeignKey('SanPham.MaSP'), primary_key=True)
    SoLuongSP = db.Column(db.Integer, nullable=False)
    DonGia = db.Column(db.Float, nullable=False)

class GioHang(db.Model):
    __tablename__ = 'GioHang'
    
    MaGioHang = db.Column(db.Integer, primary_key=True, autoincrement=True)
    MaKH = db.Column(db.Integer, db.ForeignKey('KhachHang.MaKH'))

class ChiTietGioHang(db.Model):
    __tablename__ = 'ChiTietGioHang'
    
    MaGioHang = db.Column(db.Integer, db.ForeignKey('GioHang.MaGioHang'), primary_key=True)
    MaSP = db.Column(db.Integer, db.ForeignKey('SanPham.MaSP'), primary_key=True)
    SoLuong = db.Column(db.Integer, nullable=False)

class Token(db.Model):
    __tablename__ = "Token"

    Token = db.Column(db.String, nullable=False, primary_key=True)
    LoaiToken = db.Column(db.String, nullable=False)
    ThoiDiemHetHan = db.Column(db.DateTime, nullable=False)
    MaTK = db.Column(db.String, db.ForeignKey('TaiKhoan.MaTK'))