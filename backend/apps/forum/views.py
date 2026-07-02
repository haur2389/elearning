from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import ForumPost, ForumReply
from .serializers import (
    ForumPostListSerializer, ForumPostDetailSerializer,
    ForumPostCreateSerializer, ForumReplyCreateSerializer, ForumReplySerializer
)
from apps.users.permissions import IsAdminOrInstructor, IsAdmin


class ForumPostListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # FIX: trả về array trực tiếp

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ForumPostCreateSerializer
        return ForumPostListSerializer

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        return ForumPost.objects.filter(course_id=course_id).select_related('author')


class ForumPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ForumPostDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ForumPost.objects.prefetch_related('replies__author').all()

    def get_permissions(self):
        # Chỉ Admin mới được xóa/sửa post của người khác
        if self.request.method in ['DELETE', 'PUT', 'PATCH']:
            user = self.request.user
            if user.is_authenticated and user.role == 'admin':
                return [IsAdmin()]
            # Chủ post hoặc instructor cũng được sửa/xóa post của mình
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def perform_destroy(self, instance):
        user = self.request.user
        # Admin xóa được tất cả; chủ bài chỉ xóa bài của mình
        if user.role != 'admin' and instance.author != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Bạn không có quyền xóa bài viết này.')
        instance.delete()

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()
        if user.role != 'admin' and instance.author != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Bạn không có quyền chỉnh sửa bài viết này.')
        serializer.save()


class ForumReplyCreateView(generics.CreateAPIView):
    serializer_class = ForumReplyCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class ForumReplyDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ForumReplySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ForumReply.objects.all()

    def perform_destroy(self, instance):
        user = self.request.user
        if user.role != 'admin' and instance.author != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Bạn không có quyền xóa bình luận này.')
        instance.delete()


class MarkSolutionView(generics.UpdateAPIView):
    """Instructor/Admin đánh dấu câu trả lời là giải pháp"""
    serializer_class = ForumReplySerializer
    permission_classes = [IsAdminOrInstructor]
    queryset = ForumReply.objects.all()

    def update(self, request, *args, **kwargs):
        reply = self.get_object()
        reply.is_solution = not reply.is_solution
        reply.save()
        return Response({'is_solution': reply.is_solution})
