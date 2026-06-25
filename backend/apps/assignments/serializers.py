from rest_framework import serializers
from .models import Assignment, Submission


class AssignmentSerializer(serializers.ModelSerializer):
    is_submitted = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = ['id', 'course', 'title', 'description', 'deadline',
                  'max_score', 'attachment', 'created_at', 'is_submitted']

    def get_is_submitted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.submissions.filter(student=request.user).exists()
        return False


class AssignmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['course', 'title', 'description', 'deadline', 'max_score', 'attachment']


class SubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)

    class Meta:
        model = Submission
        fields = ['id', 'assignment', 'assignment_title', 'student_name',
                  'file', 'note', 'score', 'feedback', 'status', 'submitted_at', 'graded_at']
        read_only_fields = ['score', 'feedback', 'status', 'graded_at']


class GradeSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['score', 'feedback']
