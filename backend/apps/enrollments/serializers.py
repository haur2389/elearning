from rest_framework import serializers
from .models import Enrollment
from apps.courses.serializers import CourseListSerializer


class EnrollmentSerializer(serializers.ModelSerializer):
    course_detail = CourseListSerializer(source='course', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'course_detail', 'progress', 'is_completed', 'enrolled_at', 'completed_at']
        read_only_fields = ['progress', 'is_completed', 'enrolled_at', 'completed_at']


class EnrollSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
