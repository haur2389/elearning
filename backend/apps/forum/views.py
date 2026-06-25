from rest_framework import generics, permissions
from .models import ForumPost, ForumReply
from .serializers import (
    ForumPostListSerializer, ForumPostDetailSerializer,
    ForumPostCreateSerializer, ForumReplyCreateSerializer, ForumReplySerializer
)
from apps.users.permissions import IsAdminOrInstructor


class ForumPostListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

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


class ForumReplyCreateView(generics.CreateAPIView):
    serializer_class = ForumReplyCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class MarkSolutionView(generics.UpdateAPIView):
    serializer_class = ForumReplySerializer
    permission_classes = [IsAdminOrInstructor]
    queryset = ForumReply.objects.all()

    def update(self, request, *args, **kwargs):
        reply = self.get_object()
        reply.is_solution = not reply.is_solution
        reply.save()
        return __import__('rest_framework.response', fromlist=['Response']).Response(
            {'is_solution': reply.is_solution}
        )
