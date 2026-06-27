from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from datetime import timedelta

from .models import User
from .serializers import (
    CustomTokenObtainPairSerializer, RegisterSerializer,
    UserProfileSerializer, UpdateProfileSerializer,
    ChangePasswordSerializer, ForgotPasswordSerializer,
    ResetPasswordSerializer, AdminUserSerializer
)
from .permissions import IsAdmin, IsAdminOrInstructor


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Đăng ký thành công!',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UpdateProfileSerializer
        return UserProfileSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'Cập nhật thông tin thành công!',
            'user': UserProfileSerializer(instance, context={'request': request}).data
        })


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Mật khẩu cũ không đúng.'}, status=400)

        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'message': 'Đổi mật khẩu thành công!'})


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
            otp = ''.join(random.choices(string.digits, k=6))
            user.otp_code = otp
            user.otp_expiry = timezone.now() + timedelta(minutes=10)
            user.save()

            send_mail(
                subject='Mã OTP đặt lại mật khẩu - E-Learning',
                message=f'Mã OTP của bạn là: {otp}\nMã có hiệu lực trong 10 phút.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=True,
            )
        except User.DoesNotExist:
            pass  # Không tiết lộ email tồn tại hay không

        return Response({'message': 'Nếu email tồn tại, mã OTP đã được gửi.'})


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(email=serializer.validated_data['email'])
            if user.otp_code != serializer.validated_data['otp']:
                return Response({'error': 'OTP không đúng.'}, status=400)
            if timezone.now() > user.otp_expiry:
                return Response({'error': 'OTP đã hết hạn.'}, status=400)
            user.set_password(serializer.validated_data['new_password'])
            user.otp_code = ''
            user.save()
            return Response({'message': 'Đặt lại mật khẩu thành công!'})
        except User.DoesNotExist:
            return Response({'error': 'Email không tồn tại.'}, status=404)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Đăng xuất thành công!'})
        except Exception:
            return Response({'error': 'Token không hợp lệ.'}, status=400)


# Admin views
class AdminUserListView(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminUserSerializer
    queryset = User.objects.all().order_by('-created_at')
    filterset_fields = ['role', 'is_active']
    search_fields = ['email', 'full_name', 'phone']


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminUserSerializer
    queryset = User.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({'message': 'Đã vô hiệu hóa tài khoản.'})


class AdminDashboardStatsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        from apps.courses.models import Course
        from apps.enrollments.models import Enrollment
        return Response({
            'total_students': User.objects.filter(role='student').count(),
            'total_instructors': User.objects.filter(role='instructor').count(),
            'total_courses': Course.objects.filter(status='published').count(),
            'total_enrollments': Enrollment.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'pending_courses': Course.objects.filter(status='draft').count(),
        })


class InstructorDashboardStatsView(APIView):
    """Dashboard riêng cho Giảng viên: stats khóa học của mình"""
    permission_classes = [IsAdminOrInstructor]

    def get(self, request):
        from apps.courses.models import Course
        from apps.enrollments.models import Enrollment
        from apps.assignments.models import Submission
        from apps.exams.models import ExamResult

        if request.user.role == 'admin':
            # Admin xem toàn hệ thống
            return AdminDashboardStatsView().get(request)

        # Instructor chỉ xem khóa học của mình
        my_courses = Course.objects.filter(instructor=request.user)
        my_course_ids = my_courses.values_list('id', flat=True)
        enrollments = Enrollment.objects.filter(course_id__in=my_course_ids)

        return Response({
            'total_courses': my_courses.count(),
            'published_courses': my_courses.filter(status='published').count(),
            'total_students': enrollments.values('student').distinct().count(),
            'total_enrollments': enrollments.count(),
            'completed_students': enrollments.filter(is_completed=True).count(),
            'pending_submissions': Submission.objects.filter(
                assignment__course_id__in=my_course_ids, status='submitted'
            ).count(),
        })


class InstructorProgressView(APIView):
    """Instructor theo dõi tiến độ học viên của mình"""
    permission_classes = [IsAdminOrInstructor]

    def get(self, request):
        from apps.courses.models import Course
        from apps.enrollments.models import Enrollment

        if request.user.role == 'admin':
            # Admin xem tất cả
            enrollments = Enrollment.objects.select_related('student', 'course').order_by('-enrolled_at')
        else:
            # Instructor chỉ xem học viên trong khóa mình dạy
            my_course_ids = Course.objects.filter(
                instructor=request.user
            ).values_list('id', flat=True)
            enrollments = Enrollment.objects.filter(
                course_id__in=my_course_ids
            ).select_related('student', 'course').order_by('-enrolled_at')

        from apps.enrollments.serializers import EnrollmentSerializer
        return Response(EnrollmentSerializer(enrollments[:50], many=True).data)
