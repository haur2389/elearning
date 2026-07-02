import uuid
from django.db import models
from apps.users.models import User
from apps.courses.models import Course


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    progress = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'enrollments'
        unique_together = ['student', 'course']
        verbose_name = 'Đăng ký khóa học'
        verbose_name_plural = 'Đăng ký khóa học'

    def __str__(self):
        return f"{self.student.full_name} -> {self.course.title}"

    def save(self, *args, **kwargs):
        if self.progress >= 100 and not self.is_completed:
            from django.utils import timezone
            self.is_completed = True
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ thanh toán'),
        ('completed', 'Thành công'),
        ('failed', 'Thất bại'),
        ('refunded', 'Đã hoàn tiền'),
    ]
    METHOD_CHOICES = [
        ('momo', 'MoMo'),
        ('vnpay', 'VNPay'),
        ('zalopay', 'ZaloPay'),
        ('bank_transfer', 'Chuyển khoản ngân hàng'),
        ('free', 'Miễn phí'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='free')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        verbose_name = 'Thanh toán'
        verbose_name_plural = 'Thanh toán'

    def __str__(self):
        return f"{self.student.full_name} - {self.course.title} - {self.amount}đ ({self.status})"


class Certificate(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    certificate_code = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'certificates'
        unique_together = ['student', 'course']
        ordering = ['-issued_at']
        verbose_name = 'Chứng chỉ'
        verbose_name_plural = 'Chứng chỉ'

    def __str__(self):
        return f"Chứng chỉ: {self.student.full_name} - {self.course.title}"
