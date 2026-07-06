from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from .models import Review
from .serializers import ReviewSerializer
from apps.users.permissions import IsAdminOrInstructor


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    pagination_class = None  # FIX: trả về array

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        return Review.objects.filter(course_id=course_id).select_related('student').order_by('-created_at')

    def create(self, request, *args, **kwargs):
        # Chặn admin/instructor viết đánh giá (chỉ sinh viên)
        if request.user.role in ['admin', 'instructor']:
            return Response({'error': 'Giảng viên và Admin không thể viết đánh giá.'}, status=403)
        return super().create(request, *args, **kwargs)


class ReviewReplyView(APIView):
    """Giảng viên/Admin phản hồi đánh giá của sinh viên"""
    permission_classes = [IsAdminOrInstructor]

    def patch(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return Response({'error': 'Đánh giá không tồn tại.'}, status=404)

        reply = request.data.get('instructor_reply', '').strip()
        if not reply:
            return Response({'error': 'Vui lòng nhập nội dung phản hồi.'}, status=400)

        review.instructor_reply = reply
        review.replied_at = timezone.now()
        review.save()
        return Response({'message': 'Đã gửi phản hồi!', 'review': ReviewSerializer(review).data})


class ReviewDeleteView(generics.DestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Review.objects.none()
        return Review.objects.filter(student=self.request.user)
