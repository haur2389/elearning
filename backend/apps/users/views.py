from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from django.db.models import Sum, Avg
from django.core.mail import send_mail
from django.conf import settings
import random
import string
import logging
import traceback
import requests
from datetime import timedelta

logger = logging.getLogger(__name__)


def send_email_via_brevo(to_email, subject, text_content):
    """
    Gửi email qua Brevo HTTP API (cổng 443) thay vì SMTP (cổng 587)
    vì Render free tier chặn traffic ra ngoài ở các cổng SMTP.
    Trả về (True, None) nếu thành công, (False, "lý do lỗi") nếu thất bại.
    """
    if not settings.BREVO_API_KEY:
        return False, 'Thiếu BREVO_API_KEY trong biến môi trường.'

    try:
        resp = requests.post(
            'https://api.brevo.com/v3/smtp/email',
            headers={
                'api-key': settings.BREVO_API_KEY,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            json={
                'sender': {
                    'name': settings.BREVO_SENDER_NAME,
                    'email': settings.BREVO_SENDER_EMAIL,
                },
                'to': [{'email': to_email}],
                'subject': subject,
                'textContent': text_content,
            },
            timeout=15,
        )
        if resp.status_code in (200, 201):
            return True, None
        return False, f'Brevo tra ve status {resp.status_code}: {resp.text}'
    except Exception as e:
        return False, str(e)

from .models import User
from .serializers import (
    CustomTokenObtainPairSerializer, RegisterSerializer,
    UserProfileSerializer, UpdateProfileSerializer,
    ChangePasswordSerializer, ForgotPasswordSerializer,
    ResetPasswordSerializer, AdminUserSerializer, ContactMessageSerializer
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

            ok, err = send_email_via_brevo(
                to_email=email,
                subject='Mã OTP đặt lại mật khẩu - E-Learning',
                text_content=f'Mã OTP của bạn là: {otp}\nMã có hiệu lực trong 10 phút.',
            )
            if ok:
                logger.info(f'[OTP] Gui thanh cong qua Brevo cho {email}')
                print(f'[OTP] Gui thanh cong qua Brevo cho {email}', flush=True)
            else:
                # In lỗi thật ra Render Logs để debug thay vì nuốt lỗi im lặng
                print(f'[OTP][LOI GUI MAIL - BREVO] {err}', flush=True)
                logger.error(f'[OTP] Gui mail that bai cho {email}: {err}')
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


class ContactMessageView(APIView):
    """Nhận tin nhắn từ trang Liên hệ (contact.html) và gửi tới email hỗ trợ qua Brevo."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        subject = f"[Liên hệ website] {data.get('subject') or 'Không có tiêu đề'}"
        content = (
            f"Họ tên: {data['name']}\n"
            f"Email: {data['email']}\n\n"
            f"Nội dung:\n{data['message']}"
        )

        ok, err = send_email_via_brevo(
            to_email=settings.SUPPORT_EMAIL,
            subject=subject,
            text_content=content,
        )
        if ok:
            logger.info(f"[CONTACT] Gui thanh cong tu {data['email']}")
            print(f"[CONTACT] Gui thanh cong tu {data['email']}", flush=True)
        else:
            print(f"[CONTACT][LOI GUI MAIL - BREVO] {err}", flush=True)
            logger.error(f"[CONTACT] Gui that bai tu {data['email']}: {err}")
            return Response({'error': 'Gửi liên hệ thất bại, vui lòng thử lại sau.'}, status=502)

        return Response({'message': 'Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi sớm nhất có thể.'})


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
        from apps.enrollments.models import Enrollment, Payment, Certificate
        from apps.exams.models import ExamResult

        # FIX: dashboard admin trước đây chỉ trả về 6 số liệu cơ bản, trong
        # khi hệ thống có nhiều khu vực quản lý khác (thanh toán, chứng chỉ,
        # kỳ thi) nhưng không hề có tổng quan nào trên Dashboard — admin phải
        # tự vào từng trang mới biết. Bổ sung thêm các số liệu tổng hợp quan
        # trọng để Dashboard phản ánh đúng quy mô hệ thống.
        completed_payments = Payment.objects.filter(status='completed')
        total_revenue = completed_payments.aggregate(total=Sum('amount'))['total'] or 0
        pending_payments = Payment.objects.filter(status='pending').count()

        exam_results = ExamResult.objects.all()
        avg_score = exam_results.aggregate(avg=Avg('score'))['avg'] or 0
        pass_rate = (
            exam_results.filter(is_passed=True).count() / exam_results.count() * 100
            if exam_results.count() else 0
        )

        return Response({
            'total_students': User.objects.filter(role='student').count(),
            'total_instructors': User.objects.filter(role='instructor').count(),
            'total_courses': Course.objects.filter(status='published').count(),
            'total_enrollments': Enrollment.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'pending_courses': Course.objects.filter(status='draft').count(),
            'total_revenue': float(total_revenue),
            'pending_payments': pending_payments,
            'total_certificates': Certificate.objects.count(),
            'total_exams': ExamResult.objects.count(),
            'avg_exam_score': round(avg_score, 1),
            'pass_rate': round(pass_rate, 1),
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