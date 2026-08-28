# Hệ thống Quản lý Đồ án Môn học

Repo: https://github.com/Escanor292/KhoaCongNgheThongTin

Phần code này cài **chức năng Đăng ký đề tài (UC07)** — đúng giao diện và luồng nghiệp vụ đã thiết kế:

- Sinh viên xem danh sách đề tài đang mở, sĩ số còn / đủ
- Bấm Đăng ký → hộp thoại xác nhận
- Hệ thống chặn nếu đề tài đã đủ chỗ
- Một sinh viên chỉ được 1 đề tài / học kỳ
- Kiểm tra lại trong transaction (tránh 2 SV chiếm cùng suất cuối)

## Tài liệu phân tích & thiết kế

- [PhanTich_ThietKe_QLDoAnMonHocLHU.docx](./PhanTich_ThietKe_QLDoAnMonHocLHU.docx) — cây chức năng, use case, ERD, giao diện UC07, luồng nghiệp vụ

## Chạy local

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Mở http://127.0.0.1:5000

Lần chạy đầu tự tạo file `do_an.db` và dữ liệu mẫu.

## Tài khoản demo (mật khẩu `123456`)

| Vai trò | Đăng nhập | Họ tên |
|---|---|---|
| Sinh viên | `2112345` | Nguyễn Văn An |
| Sinh viên | `2112346` | Trần Thị Bình |
| Sinh viên | `2112347` | Lê Minh Cường |
| Giảng viên | `gv001` | TS. Trần Minh Đức |

## Thử nhanh UC07

1. Đăng nhập `2112345`
2. Lọc **Còn chỗ** — đề tài Android đã đủ nên nút bị khóa
3. Bấm **Đăng ký** đề tài web → xác nhận
4. Vào **Đề tài của tôi**
5. Đăng xuất, đăng nhập `2112345` lần nữa: banner báo đã có đề tài, mọi nút Đăng ký khóa

## Cấu trúc

```
app.py                 # Flask + SQLite, nghiệp vụ UC07
templates/login.html
templates/de_tai.html          # danh sách + modal xác nhận
templates/chi_tiet.html
templates/de_tai_cua_toi.html
templates/gv_de_tai.html
static/style.css
```
