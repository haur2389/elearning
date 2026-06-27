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
