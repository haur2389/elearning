from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Enrollment, Payment, Certificate
from .serializers import (
    EnrollmentSerializer, EnrollSerializer,
    PaymentSerializer, CertificateSerializer,
)
from apps.courses.models import Course
from apps.users.permissions import IsAdmin


class EnrollView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Chỉ sinh viên mới được đăng ký khóa học
        if request.user.role in ['admin', 'instructor']:
            return Response(
                {'error': 'Admin và Giảng viên không thể đăng ký học. Vui lòng dùng tài khoản sinh viên.'},
                status=403
            )

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

        # Tự động tạo Payment record (miễn phí hoặc đã thanh toán)
        price = float(course.price) if course.price else 0
        Payment.objects.get_or_create(
            student=request.user,
            course=course,
            defaults={
                'amount': price,
                'method': 'free' if price == 0 else 'bank_transfer',
                'status': 'completed',
                'paid_at': timezone.now(),
            }
        )

        return Response({
            'message': f'Đăng ký khóa học "{course.title}" thành công!',
            'enrollment': EnrollmentSerializer(enrollment).data
        }, status=201)


class MyEnrollmentsView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Enrollment.objects.none()
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


# ── Payment Views ─────────────────────────────────────────────────────

class MyPaymentsView(generics.ListAPIView):
    """Lịch sử thanh toán của sinh viên đang đăng nhập"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Payment.objects.none()
        return Payment.objects.filter(
            student=self.request.user
        ).select_related('course').order_by('-created_at')


class AdminPaymentListView(generics.ListAPIView):
    """Admin xem tất cả giao dịch"""
    serializer_class = PaymentSerializer
    permission_classes = [IsAdmin]
    queryset = Payment.objects.all().select_related('student', 'course').order_by('-created_at')
    filterset_fields = ['status', 'method', 'course']
    search_fields = ['student__email', 'student__full_name', 'course__title', 'transaction_id']


class AdminPaymentUpdateView(APIView):
    """Admin cập nhật trạng thái thanh toán"""
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            payment = Payment.objects.get(pk=pk)
        except Payment.DoesNotExist:
            return Response({'error': 'Không tìm thấy giao dịch.'}, status=404)

        new_status = request.data.get('status')
        if new_status not in ['pending', 'completed', 'failed', 'refunded']:
            return Response({'error': 'Trạng thái không hợp lệ.'}, status=400)

        payment.status = new_status
        if new_status == 'completed' and not payment.paid_at:
            payment.paid_at = timezone.now()
        payment.save()
        return Response(PaymentSerializer(payment).data)


# ── Certificate Views ─────────────────────────────────────────────────

class MyCertificatesView(generics.ListAPIView):
    """Danh sách chứng chỉ của sinh viên"""
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Certificate.objects.none()
        return Certificate.objects.filter(
            student=self.request.user
        ).select_related('course').order_by('-issued_at')


class IssueCertificateView(APIView):
    """Cấp chứng chỉ khi hoàn thành khóa học (tự động hoặc admin cấp)"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        course_id = request.data.get('course_id')
        if not course_id:
            return Response({'error': 'Thiếu course_id.'}, status=400)

        try:
            enrollment = Enrollment.objects.get(
                student=request.user, course_id=course_id
            )
        except Enrollment.DoesNotExist:
            return Response({'error': 'Bạn chưa đăng ký khóa học này.'}, status=404)

        if not enrollment.is_completed:
            return Response(
                {'error': f'Bạn cần hoàn thành 100% khóa học trước. Hiện tại: {enrollment.progress}%.'},
                status=400
            )

        cert, created = Certificate.objects.get_or_create(
            student=request.user,
            course_id=course_id,
        )
        return Response({
            'message': 'Chứng chỉ đã được cấp!' if created else 'Bạn đã có chứng chỉ này rồi.',
            'certificate': CertificateSerializer(cert).data,
        }, status=201 if created else 200)


class AdminCertificateListView(generics.ListAPIView):
    """Admin xem tất cả chứng chỉ"""
    serializer_class = CertificateSerializer
    permission_classes = [IsAdmin]
    queryset = Certificate.objects.all().select_related('student', 'course').order_by('-issued_at')
    search_fields = ['student__email', 'student__full_name', 'course__title', 'certificate_code']
