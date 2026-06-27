from django.db import models
from apps.courses.models import Course
from apps.users.models import User


class Exam(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exams')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=30)
    total_questions = models.PositiveIntegerField(default=10)
    pass_score = models.PositiveIntegerField(default=50, help_text='Điểm đạt (%)')
    is_random = models.BooleanField(default=True, help_text='Random câu hỏi')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'exams'
        verbose_name = 'Đề thi'
        verbose_name_plural = 'Đề thi'

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Question(models.Model):
    TYPE_CHOICES = [
        ('multiple_choice', 'Trắc nghiệm'),
        ('true_false', 'Đúng/Sai'),
        ('fill_blank', 'Điền khuyết'),
        ('essay', 'Tự luận'),
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    content = models.TextField()
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='multiple_choice')
    option_a = models.CharField(max_length=500, blank=True)
    option_b = models.CharField(max_length=500, blank=True)
    option_c = models.CharField(max_length=500, blank=True)
    option_d = models.CharField(max_length=500, blank=True)
    correct_answer = models.CharField(max_length=500)
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'questions'
        verbose_name = 'Câu hỏi'
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.content[:50]}"


class ExamResult(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_results')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    score = models.FloatField(default=0)
    total_points = models.PositiveIntegerField(default=0)
    earned_points = models.PositiveIntegerField(default=0)
    is_passed = models.BooleanField(default=False)
    answers = models.JSONField(default=dict)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.PositiveIntegerField(default=0, help_text='Giây')

    class Meta:
        db_table = 'exam_results'
        verbose_name = 'Kết quả thi'

    def __str__(self):
        return f"{self.student.full_name} - {self.exam.title}: {self.score}%"
