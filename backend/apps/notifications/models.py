from django.db import models
from apps.users.models import User


class Notification(models.Model):
    TYPE_CHOICES = [
        ('new_lesson', 'Bài học mới'),
        ('new_assignment', 'Bài tập mới'),
        ('assignment_graded', 'Đã chấm bài'),
        ('exam_result', 'Kết quả thi'),
        ('new_reply', 'Trả lời mới'),
        ('system', 'Hệ thống'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notif_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='system')
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        verbose_name = 'Thông báo'

    def __str__(self):
        return f"{self.user.email} - {self.title}"
