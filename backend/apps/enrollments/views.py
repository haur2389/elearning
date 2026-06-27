from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Enrollment
from .serializers import EnrollmentSerializer, EnrollSerializer
from apps.courses.models import Course
from apps.users.permissions import IsAdmin


class EnrollView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Chỉ sinh viên mới được đăng ký khóa học
        if request.user.role in ['admin', 'instructor']:
            return Response({'error': 'Admin và Giảng viên không thể đăng ký học. Vui lòng dùng tài khoản sinh viên.'}, status=403)

        serializer = EnrollSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course_id = serializer.validated_data['course_id']

        try:
            course = Course.objects.get(pk=course_id, status='published')
        except Course.DoesNotExist:
            return Response({'error': 'Khóa học không tồn tại.'}, status=404)

        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user, course=course
        )
        if not created:
            return Response({'error': 'Bạn đã đăng ký khóa học này rồi.'}, status=400)

        return Response({
            'message': f'Đăng ký khóa học "{course.title}" thành công!',
            'enrollment': EnrollmentSerializer(enrollment).data
        }, status=201)


class MyEnrollmentsView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user
        ).select_related('course__instructor', 'course__category').order_by('-enrolled_at')


class UnenrollView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, course_id):
        try:
            enrollment = Enrollment.objects.get(student=request.user, course_id=course_id)
            enrollment.delete()
            return Response({'message': 'Hủy đăng ký thành công.'})
        except Enrollment.DoesNotExist:
            return Response({'error': 'Bạn chưa đăng ký khóa học này.'}, status=404)


class AdminEnrollmentListView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAdmin]
    queryset = Enrollment.objects.all().select_related('student', 'course').order_by('-enrolled_at')
    filterset_fields = ['course', 'is_completed']
    search_fields = ['student__email', 'student__full_name', 'course__title']
