from django.db import models
from apps.courses.models import Course
from apps.users.models import User


class ForumPost(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='forum_posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'forum_posts'
        ordering = ['-is_pinned', '-created_at']
        verbose_name = 'Bài đăng diễn đàn'

    def __str__(self):
        return self.title


class ForumReply(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_replies')
    content = models.TextField()
    is_solution = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'forum_replies'
        ordering = ['created_at']
        verbose_name = 'Trả lời diễn đàn'
