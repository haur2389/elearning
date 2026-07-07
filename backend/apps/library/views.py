from django.shortcuts import render
from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book
from .serializers import BookSerializer
from apps.users.permissions import IsAdmin


class BookListView(generics.ListAPIView):
    """Danh sách sách/tài liệu — công khai, ai cũng xem được (miễn phí)."""
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Book.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['title', 'author', 'description']
    ordering_fields = ['created_at', 'title']


class BookDetailView(generics.RetrieveAPIView):
    """Chi tiết 1 sách — công khai."""
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Book.objects.all()


class BookCategoryListView(generics.GenericAPIView):
    """Danh sách các danh mục (category) đang có trong thư viện, kèm số lượng sách."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from django.db.models import Count
        cats = (
            Book.objects.exclude(category='')
            .values('category')
            .annotate(book_count=Count('id'))
            .order_by('category')
        )
        return Response(list(cats))


class AdminBookListCreateView(generics.ListCreateAPIView):
    """Admin: xem danh sách + thêm sách mới vào thư viện."""
    serializer_class = BookSerializer
    permission_classes = [IsAdmin]
    queryset = Book.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'author']


class AdminBookDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin: sửa/xóa 1 sách."""
    serializer_class = BookSerializer
    permission_classes = [IsAdmin]
    queryset = Book.objects.all()
