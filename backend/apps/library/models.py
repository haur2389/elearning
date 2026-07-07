from django.db import models


class Book(models.Model):
    """Sách / tài liệu tham khảo trong Thư viện — độc lập hoàn toàn với Course.
    Tất cả sách trong thư viện đều xem MIỄN PHÍ."""
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True, help_text='Vd: Lập trình, Cơ sở dữ liệu, Kỹ năng mềm...')
    cover_url = models.CharField(max_length=500, blank=True, help_text='URL ảnh bìa sách')
    file_url = models.CharField(max_length=500, help_text='URL file PDF/tài liệu để xem/tải (Google Drive, v.v.)')
    pages = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'library_books'
        ordering = ['-created_at']
        verbose_name = 'Sách / Tài liệu'
        verbose_name_plural = 'Sách / Tài liệu'

    def __str__(self):
        return self.title
