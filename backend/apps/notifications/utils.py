"""
Helper functions để tạo thông báo (Notification) từ các app khác
(lessons, exams, assignments, enrollments...) mà không cần mỗi nơi tự
import Notification và tự viết lại logic lấy danh sách người nhận.

Dùng bulk_create khi gửi cho nhiều người (vd toàn bộ học viên đã đăng ký
1 khóa học) để tránh N query riêng lẻ khi khóa học có nhiều học viên.
"""
from .models import Notification


def notify(user, title, message, notif_type='system', link=''):
    """Tạo 1 thông báo cho 1 user. Bỏ qua an toàn nếu user=None."""
    if not user:
        return
    Notification.objects.create(
        user=user, title=title, message=message,
        notif_type=notif_type, link=link,
    )


def notify_many(users, title, message, notif_type='system', link=''):
    """Tạo thông báo giống nhau cho nhiều user cùng lúc (1 query)."""
    users = [u for u in users if u]
    if not users:
        return
    Notification.objects.bulk_create([
        Notification(user=u, title=title, message=message,
                      notif_type=notif_type, link=link)
        for u in users
    ])


def notify_enrolled_students(course, title, message, notif_type='system', link=''):
    """Báo cho toàn bộ học viên đang học 1 khóa học (dùng khi giảng viên
    thêm bài học / bài tập / đề thi mới cho khóa học đó)."""
    from apps.users.models import User
    from apps.enrollments.models import Enrollment
    student_ids = Enrollment.objects.filter(course=course).values_list('student_id', flat=True)
    students = User.objects.filter(id__in=student_ids)
    notify_many(students, title, message, notif_type, link)


def notify_admins(title, message, notif_type='system', link=''):
    """Báo cho toàn bộ tài khoản admin trong hệ thống."""
    from apps.users.models import User
    admins = User.objects.filter(role='admin')
    notify_many(admins, title, message, notif_type, link)
