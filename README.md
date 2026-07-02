# 🎓 Smart E-Learning - Hệ thống học trực tuyến ĐH Bình Dương

## 📋 Tổng quan

Hệ thống E-Learning đầy đủ với Django REST Framework (Backend) + HTML/JS thuần (Frontend).

**Demo:** https://smart-elearning-chen-woei-haur.vercel.app  
**API:** https://elearning-backend-ead6.onrender.com

---

## 🏗️ Cấu trúc dự án

```
elearning/
├── backend/                    # Django REST API
│   ├── apps/
│   │   ├── users/             # Xác thực, phân quyền, AI chatbot
│   │   ├── courses/           # Khóa học, danh mục, chương
│   │   ├── lessons/           # Bài học (video/pdf/text)
│   │   ├── enrollments/       # Đăng ký khóa học
│   │   ├── assignments/       # Bài tập
│   │   ├── exams/             # Bài thi trắc nghiệm
│   │   ├── reviews/           # Đánh giá khóa học
│   │   ├── forum/             # Diễn đàn thảo luận
│   │   └── notifications/     # Thông báo
│   ├── core/                  # Settings, URLs chính
│   └── requirements.txt
├── frontend/                  # HTML/CSS/JS thuần
│   ├── index.html            # Trang chủ
│   ├── courses.html          # Danh sách khóa học
│   ├── course-detail.html    # Chi tiết khóa học
│   ├── learn.html            # Giao diện học
│   ├── exam.html             # Làm bài thi
│   ├── admin/                # Trang quản trị Admin
│   ├── instructor/           # Trang giảng viên
│   └── js/
│       ├── config.js         # Cấu hình API URL + helpers
│       └── wake-up.js        # Wake up Render free tier
└── README.md
```

---

## 👥 Phân quyền

| Tính năng | Admin | Giảng viên | Sinh viên |
|-----------|-------|------------|-----------|
| Quản lý người dùng | ✅ | ❌ | ❌ |
| Quản lý danh mục | ✅ | ❌ | ❌ |
| Tạo/sửa khóa học | ✅ (duyệt) | ✅ (của mình) | Xem |
| Tạo bài tập/bài thi | ✅ | ✅ | Nộp/Làm |
| Chấm điểm | ✅ | ✅ | ❌ |
| Đánh giá khóa học | ❌ | ❌ | ✅ |
| AI Chatbot | Cấu hình | Dùng | Dùng |

---

## 🚀 Deploy

### Backend (Render)

1. Tạo **PostgreSQL** database trên Render → copy Internal Database URL
2. Tạo **Web Service** → connect GitHub repo
3. Cấu hình:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py seed_data && python manage.py seed_courses_full`
   - **Start Command:** `gunicorn core.wsgi:application --bind 0.0.0.0:$PORT`
4. **Environment Variables:**
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   DATABASE_URL=postgresql://...
   ALLOWED_HOSTS=*
   CORS_ALLOWED_ORIGINS=https://your-vercel-domain.vercel.app
   GEMINI_API_KEY=your-gemini-key   # Lấy miễn phí tại aistudio.google.com
   ```

### Frontend (Vercel)

1. Sửa `frontend/js/config.js`:
   ```javascript
   const CONFIG = {
       API_BASE_URL: 'https://your-render-url.onrender.com/api',
       APP_NAME: 'Smart E-Learning',
   };
   ```
2. Import GitHub repo vào Vercel
3. **Root Directory:** `frontend`, **Framework:** Other

### Sau khi deploy

```bash
# Vào Render Shell hoặc chạy qua Build Command
python manage.py createsuperuser
```

---

## 🤖 AI Chatbot

Chatbot hỗ trợ 3 API (tự động fallback):
1. **Anthropic Claude** (`ANTHROPIC_API_KEY`)
2. **Google Gemini** (`GEMINI_API_KEY`) ← Khuyến nghị, miễn phí
3. **OpenAI GPT** (`OPENAI_API_KEY`)

Chatbot đã được nạp **170 cặp Q&A** từ tài liệu FAQ hệ thống.

Lấy Gemini API Key miễn phí: https://aistudio.google.com

---

## 🔧 Tài khoản mặc định (sau seed_data)

| Role | Email | Mật khẩu |
|------|-------|---------|
| Admin | admin@elearning.com | Admin123456 |
| Giảng viên | gv1@elearning.com | Gva123456 |
| Sinh viên | sv1@elearning.com | Sva123456 |

---

## 🐛 Các lỗi đã fix

- ✅ Bài thi 500 error (bỏ seed_data tự động trong ExamListView)
- ✅ Instructor/Admin thấy "Xem khóa học" thay vì "Đăng ký"
- ✅ Khóa học mới tạo mặc định status=published (hiện ngay với sinh viên)
- ✅ Đánh giá hiện sau khi submit (reload loadReviews)
- ✅ Bài tập/thi handle paginated response `{results:[]}`
- ✅ submitAssignment dùng `CONFIG.API_BASE_URL` đúng
- ✅ AI Chatbot nạp 170 Q&A từ file FAQ

---

## 📦 Cập nhật code

```bash
git add .
git commit -m "your message"
git push origin master
```

Render và Vercel tự động redeploy sau khi push.
