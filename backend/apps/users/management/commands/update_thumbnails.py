from django.core.management.base import BaseCommand
from apps.courses.models import Course


class Command(BaseCommand):
    help = 'Cập nhật thumbnail ảnh thật cho các khóa học'

    def handle(self, *args, **kwargs):
        thumbnails = [
            ('lập trình', 'https://images.unsplash.com/photo-1587620962725-abab19836100?w=800&h=400&fit=crop'),
            ('python', 'https://images.unsplash.com/photo-1587620962725-abab19836100?w=800&h=400&fit=crop'),
            ('cơ sở dữ liệu', 'https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=800&h=400&fit=crop'),
            ('web', 'https://images.unsplash.com/photo-1547658719-da2b51169166?w=800&h=400&fit=crop'),
            ('trí tuệ', 'https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=800&h=400&fit=crop'),
            ('đám mây', 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&h=400&fit=crop'),
            ('mật mã', 'https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=800&h=400&fit=crop'),
            ('an toàn', 'https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=800&h=400&fit=crop'),
            ('mạng', 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&h=400&fit=crop'),
            ('hướng đối tượng', 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&h=400&fit=crop'),
        ]
        updated = 0
        for keyword, url in thumbnails:
            qs = Course.objects.filter(title__icontains=keyword)
            if qs.exists():
                qs.update(thumbnail=url)
                updated += qs.count()
                self.stdout.write(f'  ✅ Updated {qs.count()} courses matching "{keyword}"')

        self.stdout.write(self.style.SUCCESS(f'🎉 Đã cập nhật {updated} thumbnail!'))
