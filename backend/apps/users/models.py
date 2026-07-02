from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('instructor', 'Giảng viên'),
        ('student', 'Sinh viên'),
    ]

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    otp_code = models.CharField(max_length=6, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Người dùng'

    def __str__(self):
        return f"{self.full_name or self.email} ({self.role})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_instructor(self):
        return self.role == 'instructor'

    @property
    def is_student(self):
        return self.role == 'student'
