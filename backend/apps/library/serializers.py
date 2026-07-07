from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'description', 'category',
            'cover_url', 'file_url', 'pages', 'created_at',
        ]
        read_only_fields = ['created_at']
