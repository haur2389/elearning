from rest_framework import serializers
from .models import Enrollment, Payment, Certificate
from apps.courses.serializers import CourseListSerializer


class EnrollmentSerializer(serializers.ModelSerializer):
    course_detail = CourseListSerializer(source='course', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'course_detail', 'student_name', 'student_email',
                  'progress', 'is_completed', 'enrolled_at', 'completed_at']
        read_only_fields = ['progress', 'is_completed', 'enrolled_at', 'completed_at']


class EnrollSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()


class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'student', 'student_name', 'student_email',
            'course', 'course_title', 'amount', 'method', 'method_display',
            'status', 'status_display', 'transaction_id', 'note',
            'paid_at', 'created_at',
        ]
        read_only_fields = ['created_at']


class CertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Certificate
        fields = [
            'id', 'student', 'student_name', 'student_email',
            'course', 'course_title', 'certificate_code', 'issued_at',
        ]
        read_only_fields = ['certificate_code', 'issued_at']
