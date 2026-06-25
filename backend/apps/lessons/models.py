from django.db import models
from apps.courses.models import Chapter


class Lesson(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('pdf', 'PDF'),
        ('text', 'Văn bản'),
        ('slide', 'Slide'),
    ]

    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='video')
    video_url = models.URLField(blank=True)
    pdf_file = models.FileField(upload_to='lessons/pdfs/', blank=True, null=True)
    slide_url = models.URLField(blank=True)
    content = models.TextField(blank=True)
    duration = models.PositiveIntegerField(default=0, help_text='Thời lượng (phút)')
    order = models.PositiveIntegerField(default=0)
    is_preview = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lessons'
        verbose_name = 'Bài học'
        verbose_name_plural = 'Bài học'
        ordering = ['order']

    def __str__(self):
        return f"{self.chapter.title} - {self.title}"


class LessonProgress(models.Model):
    from apps.users.models import User
    student = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    watch_percentage = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    last_watched = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lesson_progress'
        unique_together = ['student', 'lesson']
        verbose_name = 'Tiến độ bài học'

    def __str__(self):
        return f"{self.student.email} - {self.lesson.title}: {self.watch_percentage}%"
