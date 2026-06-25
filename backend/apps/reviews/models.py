from django.db import models
from apps.courses.models import Course
from apps.users.models import User


class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews'
        unique_together = ['course', 'student']
        verbose_name = 'Đánh giá'

    def __str__(self):
        return f"{self.student.full_name} - {self.course.title}: {self.rating}★"
