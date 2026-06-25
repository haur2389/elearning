# 🎓 Smart E-Learning System

> **Hệ thống Học Trực Tuyến Thông Minh** — Tiểu luận Chuyên đề 1, HK3 2025–2026  
> Trường Đại học Bình Dương | Sinh viên: **Chen Woei Haur** | MSSV: **22050056**

---

## 🌐 Demo trực tiếp (Cloud)

| Thành phần | URL | Mô tả |
|---|---|---|
| 🖥️ **Frontend** | [elearning-ten-zeta.vercel.app](https://elearning-ten-zeta.vercel.app) | Giao diện người dùng |
| ⚙️ **Backend API** | [elearning-backend-ead0.onrender.com](https://elearning-backend-ead0.onrender.com) | Django REST API |
| 📄 **API Docs** | [/api/docs/](https://elearning-backend-ead0.onrender.com/api/docs/) | Swagger UI |
| 🔧 **Admin** | [/admin/](https://elearning-backend-ead0.onrender.com/admin/) | Django Admin |

> ⚠️ Backend chạy trên Render Free — lần đầu truy cập có thể chờ 30-50 giây để khởi động

---

## 🔑 Tài khoản Demo

| Vai trò | Email | Mật khẩu |
|---|---|---|
| 👑 Admin | admin@elearning.com | Admin@123 |
| 👨‍🏫 Giảng viên | gv1@elearning.com | Gv@123456 |
| 👨‍🎓 Sinh viên | sv1@elearning.com | Sv@123456 |

---

## 🏗️ Kiến trúc hệ thống (3 tầng)

```
┌─────────────────────────────────────────────────────┐
│           TẦNG 1: FRONTEND (Presentation)            │
│         HTML5 + TailwindCSS + JavaScript             │
│              Deploy: Vercel (CDN)                    │
└─────────────────────┬───────────────────────────────┘
                      │ HTTPS / REST API (JSON)
┌─────────────────────▼───────────────────────────────┐
│           TẦNG 2: BACKEND (Business Logic)           │
│         Python Django + Django REST Framework        │
│         JWT Authentication + Phân quyền 3 cấp       │
│              Deploy: Render (Cloud)                  │
└─────────────────────┬───────────────────────────────┘
                      │ SQL / Django ORM
┌─────────────────────▼───────────────────────────────┐
│           TẦNG 3: DATABASE (Data Layer)              │
│              PostgreSQL 15 — 12 bảng                │
│              Deploy: Render PostgreSQL               │
└─────────────────────────────────────────────────────┘
```

---

## 📦 Công nghệ sử dụng

| Layer | Công nghệ | Phiên bản |
|---|---|---|
| Frontend | HTML5 + TailwindCSS + JavaScript | ES6+ |
| Backend | Python + Django | 4.2.7 |
| API | Django REST Framework | 3.14.0 |
| Auth | JWT (djangorestframework-simplejwt) | 5.3.0 |
| Database | PostgreSQL | 15 |
| AI Chatbot | Google Gemini API | 1.5-flash |
| Deploy FE | Vercel | Latest |
| Deploy BE | Render | Free tier |
| Container | Docker + Docker Compose | Latest |

---

## 🎯 Chức năng chính

### 👑 Admin
- Quản lý người dùng (khóa/mở tài khoản, đổi vai trò)
- Quản lý khóa học và danh mục
- Xem Dashboard thống kê + biểu đồ Chart.js
- Quản lý lượt đăng ký khóa học

### 👨‍🏫 Giảng viên
- Tạo và quản lý khóa học (Chương → Bài học)
- Upload video YouTube, PDF, nội dung text
- Tạo đề thi trực tuyến + ngân hàng câu hỏi
- Tạo bài tập, chấm điểm thủ công
- Theo dõi tiến độ học viên

### 👨‍🎓 Sinh viên
- Đăng ký khóa học (miễn phí / có phí)
- Thanh toán QR Code / Tiền mặt
- Học bài với video YouTube embed
- Theo dõi % tiến độ từng bài học
- Làm bài thi trực tuyến + đếm ngược
- Nộp bài tập (PDF/DOCX/ZIP)
- Đánh giá sao khóa học
- Tham gia diễn đàn hỏi đáp
- Chat với AI Chatbot

---

## 📚 Môn học CNTT - ĐH Bình Dương

| Mã môn | Tên môn | Học phí |
|---|---|---|
| INF0433 | Nhập môn lập trình (Python) | Miễn phí |
| INF0083 | Cơ sở dữ liệu (SQL) | 199.000đ |
| INF0203 | Lập trình hướng đối tượng | 299.000đ |
| INF0243 | Lập trình Web (HTML/CSS/JS) | 399.000đ |
| INF0103 | Nhập môn Trí tuệ nhân tạo | 499.000đ |
| INF1003 | Điện toán đám mây | 399.000đ |
| INF0893 | Mật mã và An toàn thông tin | 349.000đ |

---

## 🗄️ Cơ sở dữ liệu (12 bảng)

```
users           → Tài khoản người dùng (3 vai trò)
categories      → Danh mục khóa học
courses         → Khóa học
chapters        → Chương học
lessons         → Bài học (video/PDF/text)
lesson_progress → Tiến độ xem từng bài
enrollments     → Đăng ký khóa học
exams           → Đề thi
questions       → Ngân hàng câu hỏi
exam_results    → Kết quả thi
assignments     → Bài tập
reviews         → Đánh giá sao
```

---

## 🚀 Chạy local bằng Docker

```bash
# 1. Clone repo
git clone https://github.com/haur2389/elearning.git
cd elearning

# 2. Tạo file .env
cp backend/.env.example backend/.env

# 3. Chạy Docker Compose
docker-compose up --build

# 4. Truy cập
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000/api/docs/
```

---

## 📁 Cấu trúc project

```
elearning/
├── backend/                 ← Django REST Framework
│   ├── apps/
│   │   ├── users/           ← Auth, JWT, phân quyền
│   │   ├── courses/         ← Khóa học, danh mục, chương
│   │   ├── lessons/         ← Bài học, tiến độ
│   │   ├── enrollments/     ← Đăng ký khóa học
│   │   ├── exams/           ← Thi trực tuyến
│   │   ├── assignments/     ← Bài tập
│   │   ├── reviews/         ← Đánh giá
│   │   ├── notifications/   ← Thông báo
│   │   └── forum/           ← Diễn đàn
│   ├── core/                ← Settings, URLs
│   ├── requirements.txt
│   └── Procfile             ← Render deploy config
├── frontend/                ← HTML + TailwindCSS + JS
│   ├── index.html           ← Trang chủ
│   ├── courses.html         ← Danh sách khóa học
│   ├── course-detail.html   ← Chi tiết khóa học
│   ├── learn.html           ← Trang học bài
│   ├── exam.html            ← Thi trực tuyến
│   ├── payment.html         ← Thanh toán QR/tiền mặt
│   ├── admin/               ← Trang quản trị
│   ├── instructor/          ← Trang giảng viên
│   └── js/config.js         ← API config
├── docker-compose.yml
└── render.yaml              ← Render deploy config
```

---

## 🔌 API Endpoints (30+)

Xem đầy đủ tại: **[/api/docs/](https://elearning-backend-ead0.onrender.com/api/docs/)**

| Method | Endpoint | Mô tả |
|---|---|---|
| POST | /api/auth/register/ | Đăng ký tài khoản |
| POST | /api/auth/login/ | Đăng nhập → JWT |
| GET | /api/courses/ | Danh sách khóa học |
| POST | /api/enrollments/enroll/ | Đăng ký khóa học |
| GET | /api/exams/{id}/ | Lấy đề thi |
| POST | /api/exams/{id}/submit/ | Nộp bài thi |
| POST | /api/ai/chat/ | AI Chatbot |

---

## ☁️ Triển khai Cloud

```
Vercel (Frontend CDN)
    ↓ HTTPS
Render Web Service (Django + Gunicorn)
    ↓ SQL
Render PostgreSQL Database
```

**Tự động deploy:** Mỗi lần `git push` lên GitHub, Render và Vercel tự động build và deploy lại.

---

## 👤 Thông tin sinh viên

- **Họ tên:** Chen Woei Haur  
- **MSSV:** 22050056  
- **Môn học:** Chuyên đề 1 — HK3 năm học 2025–2026  
- **Trường:** Đại học Bình Dương  
- **GitHub:** [@haur2389](https://github.com/haur2389)
