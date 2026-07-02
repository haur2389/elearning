from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg
from .models import Category, Course, Chapter
from .serializers import (
    CategorySerializer, CourseListSerializer, CourseDetailSerializer,
    CourseCreateUpdateSerializer, ChapterSerializer
)
from apps.users.permissions import IsAdmin, IsInstructor, IsAdminOrInstructor


class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None  # FIX: trả về array thẳng, không paginate

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsAdmin()]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsAdmin()]


class CourseListView(generics.ListAPIView):
    serializer_class = CourseListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'level', 'status']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'price', 'title']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return super().get_queryset().none()
        queryset = Course.objects.select_related('instructor', 'category')
        user = self.request.user
        if user.is_authenticated and user.role in ['admin']:
            return queryset
        if user.is_authenticated and user.role == 'instructor':
            return queryset.filter(status='published') | queryset.filter(instructor=user)
        return queryset.filter(status='published')


class CourseDetailView(generics.RetrieveAPIView):
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'pk'

    def get_queryset(self):
        return Course.objects.prefetch_related('chapters__lessons').select_related('instructor', 'category')


class CourseCreateView(generics.CreateAPIView):
    serializer_class = CourseCreateUpdateSerializer
    permission_classes = [IsAdminOrInstructor]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)


class CourseUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseCreateUpdateSerializer
    permission_classes = [IsAdminOrInstructor]

    def get_queryset(self):
        # Fix: tránh lỗi khi drf_yasg generate schema (không có request user thật)
        if getattr(self, 'swagger_fake_view', False):
            return Course.objects.none()
        user = self.request.user
        if user.role == 'admin':
            return Course.objects.all()
        return Course.objects.filter(instructor=user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 'archived'
        instance.save()
        return Response({'message': 'Khóa học đã được lưu trữ.'})


class InstructorCourseListView(generics.ListAPIView):
    serializer_class = CourseListSerializer
    permission_classes = [IsAdminOrInstructor]
    pagination_class = None  # FIX: instructor xem tất cả khóa của mình

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Course.objects.none()
        if self.request.user.role == 'admin':
            return Course.objects.all().order_by('-created_at')
        return Course.objects.filter(instructor=self.request.user).order_by('-created_at')


# Chapter views
class ChapterListCreateView(generics.ListCreateAPIView):
    serializer_class = ChapterSerializer
    permission_classes = [IsAdminOrInstructor]
    pagination_class = None  # FIX: trả về array

    def get_queryset(self):
        return Chapter.objects.filter(course_id=self.kwargs['course_id'])

    def perform_create(self, serializer):
        course = Course.objects.get(pk=self.kwargs['course_id'])
        serializer.save(course=course)


class ChapterDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChapterSerializer
    permission_classes = [IsAdminOrInstructor]
    queryset = Chapter.objects.all()
