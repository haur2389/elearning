# API DOCUMENTATION
## Hệ thống Học trực tuyến thông minh (Smart E-Learning)

**Backend:** Django REST Framework
**Base URL (local):** `http://localhost:8000/api`
**Base URL (production):** `https://elearning-backend-ead6.onrender.com/api`
**Interactive docs (đã tích hợp sẵn trong source code):**
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`

**Xác thực:** JWT (JSON Web Token) qua `djangorestframework-simplejwt`.
Gửi kèm header cho các endpoint yêu cầu đăng nhập:
```
Authorization: Bearer <access_token>
```

**Phân quyền (roles):** `admin`, `instructor`, `student` — được kiểm tra qua custom permission classes `IsAdmin`, `IsAdminOrInstructor`, `IsAuthenticated`.

**Định dạng phản hồi:** JSON. Lỗi trả về dạng:
```json
{ "detail": "Thông báo lỗi" }
```
---

## 1. Auth & User — `/api/auth/`

| Method | Endpoint | Quyền truy cập | Mô tả |
|---|---|---|---|
| POST | `/api/auth/register/` | Public | Đăng ký tài khoản mới |
| POST | `/api/auth/login/` | Public | Đăng nhập, trả về `access` + `refresh` token |
| POST | `/api/auth/logout/` | Đã đăng nhập | Đăng xuất (blacklist refresh token) |
| POST | `/api/auth/token/refresh/` | Public | Làm mới access token bằng refresh token |
| GET/PUT | `/api/auth/profile/` | Đã đăng nhập | Xem / cập nhật hồ sơ cá nhân |
| POST | `/api/auth/change-password/` | Đã đăng nhập | Đổi mật khẩu |
| POST | `/api/auth/forgot-password/` | Public | Gửi OTP quên mật khẩu qua email |
| POST | `/api/auth/reset-password/` | Public | Đặt lại mật khẩu bằng OTP |
| GET/POST | `/api/auth/admin/users/` | Admin | Danh sách / tạo người dùng |
| GET/PUT/DELETE | `/api/auth/admin/users/{id}/` | Admin | Xem / sửa / xóa người dùng |
| GET | `/api/auth/admin/dashboard/` | Admin | Thống kê tổng quan hệ thống |
| GET | `/api/auth/instructor/dashboard/` | Admin/Instructor | Thống kê giảng viên |
| GET | `/api/auth/instructor/progress/` | Admin/Instructor | Tiến độ học viên |

### AI Chatbot — `/api/ai/`
| Method | Endpoint | Quyền | Mô tả |
|---|---|---|---|
| POST | `/api/ai/chat/` | Đã đăng nhập | Gửi câu hỏi tới AI chatbot (Google Gemini) |

---

## 2. Courses — `/api/courses/`

| Method | Endpoint | Quyền | Mô tả |
|---|---|---|---|
| GET | `/api/courses/` | Public | Danh sách khóa học (filter, search, phân trang) |
| POST | `/api/courses/create/` | Admin/Instructor | Tạo khóa học mới |
| GET | `/api/courses/{id}/` | Public | Chi tiết khóa học |
| GET/PUT/DELETE | `/api/courses/{id}/update/` | Admin/Instructor (chủ sở hữu) | Cập nhật / xóa khóa học |
| GET | `/api/courses/my-courses/` | Admin/Instructor | Khóa học của giảng viên hiện tại |
| GET/POST | `/api/courses/{course_id}/chapters/` | Admin/Instructor (ghi) | Danh sách / tạo chương |
| GET/PUT/DELETE | `/api/courses/chapters/{id}/` | Admin/Instructor | Chi tiết / sửa / xóa chương |
| GET/POST | `/api/courses/categories/` | Public (đọc) / Admin (ghi) | Danh mục khóa học |
| GET/PUT/DELETE | `/api/courses/categories/{id}/` | Public (đọc) / Admin (ghi) | Chi tiết danh mục |

---

## 3. Lessons — `/api/lessons/`

| Method | Endpoint | Quyền | Mô tả |
|---|---|---|---|
| GET | `/api/lessons/{id}/` | Đã đăng nhập | Chi tiết bài học (video/pdf/text/slide) |
| POST | `/api/lessons/create/` | Admin/Instructor | Tạo bài học |
| GET/PUT/DELETE | `/api/lessons/{id}/update/` | Admin/Instructor | Sửa / xóa bài học |
| POST | `/api/lessons/{lesson_id}/progress/` | Đã đăng nhập | Cập nhật % tiến độ xem bài học |

---

## 4. Enrollments, Payment, Certificate — `/api/enrollments/`

| Method | Endpoint | Quyền | Mô tả |
|---|---|---|---|
| POST | `/api/enrollments/enroll/` | Đã đăng nhập | Đăng ký khóa học |
| GET | `/api/enrollments/my/` | Đã đăng nhập | Khóa học đã đăng ký của tôi |
| DELETE | `/api/enrollments/{course_id}/unenroll/` | Đã đăng nhập | Hủy đăng ký khóa học |
| GET | `/api/enrollments/admin/all/` | Admin | Toàn bộ enrollment (quản trị) |
| GET | `/api/enrollments/payments/my/` | Đã đăng nhập | Lịch sử thanh toán của tôi |
| GET | `/api/enrollments/payments/admin/` | Admin | Toàn bộ giao dịch thanh toán |
| PATCH | `/api/enrollments/payments/{id}/update/` | Admin | Cập nhật trạng thái thanh toán |
| GET | `/api/enrollments/certificates/my/` | Đã đăng nhập | Chứng chỉ của tôi |
| POST | `/api/enrollments/certificates/issue/` | Đã đăng nhập | Cấp chứng chỉ (khi hoàn thành khóa học) |
| GET | `/api/enrollments/certificates/admin/` | Admin | Toàn bộ chứng chỉ đã cấp |

---

## 5. Assignments — `/api/assignments/`

| Method | Endpoint | Quyền | Mô tả |
|---|---|---|---|
| GET | `/api/assignments/courses/{course_id}/` | Đã đăng nhập | Danh sách bài tập của khóa học |
| POST | `/api/assignments/create/` | Admin/Instructor | Tạo bài tập |
| GET/PUT/DELETE | `/api/assignments/{id}/` | Admin/Instructor | Chi tiết / sửa / xóa bài tập |
| POST | `/api/assignments/{assignment_id}/submit/` | Đã đăng nhập | Nộp bài tập |
| GET | `/api/assignments/{assignment_id}/submissions/` | Admin/Instructor | Danh sách bài nộp |
| PATCH | `/api/assignments/submissions/{submission_id}/grade/` | Admin/Instructor | Chấm điểm bài nộp |
| GET | `/api/assignments/my-submissions/` | Đã đăng nhập | Bài nộp của tôi |

---

## 6. Exams — `/api/exams/`

| Method | Endpoint | Quyền | Mô tả |
|---|---|---|---|
| GET | `/api/exams/courses/{course_id}/` | Đã đăng nhập | Danh sách đề thi của khóa học |
| GET | `/api/exams/{id}/` | Đã đăng nhập | Chi tiết đề thi |
| POST | `/api/exams/create/` | Admin/Instructor | Tạo đề thi |
| GET/PUT/DELETE | `/api/exams/{id}/update/` | Admin/Instructor | Sửa / xóa đề thi |
| POST | `/api/exams/questions/create/` | Admin/Instructor | Thêm câu hỏi |
| GET/PUT/DELETE | `/api/exams/questions/{id}/` | Admin/Instructor | Sửa / xóa câu hỏi |
| POST | `/api/exams/{exam_id}/submit/` | Đã đăng nhập | Nộp bài thi, tự động chấm điểm |
| GET | `/api/exams/{exam_id}/results/` | Admin/Instructor | Kết quả thi của học viên |
| GET | `/api/exams/my-results/` | Đã đăng nhập | Kết quả thi của tôi |

---

## 7. Reviews — `/api/reviews/`

| Method | Endpoint | Quyền | Mô tả |
|---|---|---|---|
| GET/POST | `/api/reviews/courses/{course_id}/` | Đã đăng nhập (ghi) | Danh sách / tạo đánh giá khóa học |
| PATCH | `/api/reviews/{id}/reply/` | Admin/Instructor | Giảng viên phản hồi đánh giá |
| DELETE | `/api/reviews/{id}/delete/` | Chủ sở hữu | Xóa đánh giá |

---

## 8. Forum — `/api/forum/`

| Method | Endpoint | Quyền | Mô tả |
|---|---|---|---|
| GET/POST | `/api/forum/courses/{course_id}/` | Đã đăng nhập | Danh sách / tạo bài đăng diễn đàn |
| GET/PUT/DELETE | `/api/forum/posts/{id}/` | Đã đăng nhập | Chi tiết / sửa / xóa bài đăng |
| POST | `/api/forum/replies/create/` | Đã đăng nhập | Tạo trả lời |
| GET/PUT/DELETE | `/api/forum/replies/{id}/` | Đã đăng nhập | Chi tiết / sửa / xóa trả lời |
| PATCH | `/api/forum/replies/{id}/solution/` | Admin/Instructor | Đánh dấu câu trả lời là giải pháp |

---

## 9. Notifications — `/api/notifications/`

| Method | Endpoint | Quyền | Mô tả |
|---|---|---|---|
| GET | `/api/notifications/` | Đã đăng nhập | Danh sách thông báo của tôi |
| GET | `/api/notifications/unread/` | Đã đăng nhập | Số thông báo chưa đọc |
| POST | `/api/notifications/mark-read/` | Đã đăng nhập | Đánh dấu tất cả đã đọc |
| POST | `/api/notifications/{id}/read/` | Đã đăng nhập | Đánh dấu 1 thông báo đã đọc |

---

## Ví dụ Request / Response

### Đăng nhập
```
POST /api/auth/login/
Content-Type: application/json

{
  "email": "student1@elearning.com",
  "password": "matkhau123"
}
```
Response `200 OK`:
```json
{
  "access": "eyJhbGciOi...",
  "refresh": "eyJhbGciOi..."
}
```

### Đăng ký khóa học
```
POST /api/enrollments/enroll/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "course_id": 3
}
```
Response `201 Created`:
```json
{
  "id": 12,
  "student": 5,
  "course": 3,
  "progress": 0,
  "is_completed": false,
  "enrolled_at": "2026-07-01T08:00:00Z"
}
```

### Nộp bài thi
```
POST /api/exams/7/submit/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "answers": { "1": "A", "2": "C", "3": "B" }
}
```
Response `200 OK`:
```json
{
  "score": 80.0,
  "total_points": 10,
  "earned_points": 8,
  "is_passed": true
}
```

---

## Mã lỗi HTTP thường gặp

| Code | Ý nghĩa |
|---|---|
| 200 | Thành công |
| 201 | Tạo mới thành công |
| 400 | Dữ liệu gửi lên không hợp lệ |
| 401 | Chưa xác thực / token hết hạn |
| 403 | Không đủ quyền truy cập |
| 404 | Không tìm thấy tài nguyên |
| 500 | Lỗi server |
