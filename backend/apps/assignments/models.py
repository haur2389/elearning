from django.db import models
from apps.courses.models import Course
from apps.users.models import User


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateTimeField()
    max_score = models.PositiveIntegerField(default=100)
    attachment = models.FileField(upload_to='assignments/files/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'assignments'
        verbose_name = 'Bài tập'

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Submission(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Đã nộp'),
        ('graded', 'Đã chấm'),
        ('late', 'Nộp muộn'),
    ]

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to='submissions/')
    note = models.TextField(blank=True)
    score = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'submissions'
        unique_together = ['assignment', 'student']
        verbose_name = 'Bài nộp'

    def __str__(self):
        return f"{self.student.full_name} - {self.assignment.title}"
