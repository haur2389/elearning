from rest_framework import serializers
from .models import Assignment, Submission


class SubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)

    class Meta:
        model = Submission
        fields = ['id', 'assignment', 'assignment_title', 'student_name',
                  'file', 'note', 'score', 'feedback', 'status', 'submitted_at', 'graded_at']
        read_only_fields = ['score', 'feedback', 'status', 'graded_at']


class AssignmentSerializer(serializers.ModelSerializer):
    is_submitted = serializers.SerializerMethodField()
    my_submission = serializers.SerializerMethodField()  # FIX: trả về chi tiết bài nộp

    class Meta:
        model = Assignment
        fields = ['id', 'course', 'title', 'description', 'deadline',
                  'max_score', 'attachment', 'created_at', 'is_submitted', 'my_submission']

    def get_is_submitted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.submissions.filter(student=request.user).exists()
        return False

    def get_my_submission(self, obj):
        """Trả về thông tin bài nộp của sinh viên hiện tại (nếu có)"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                sub = obj.submissions.get(student=request.user)
                return {
                    'id': sub.id,
                    'status': sub.status,
                    'score': sub.score,
                    'feedback': sub.feedback,
                    'submitted_at': sub.submitted_at,
                    'graded_at': sub.graded_at,
                }
            except Submission.DoesNotExist:
                pass
        return None


class AssignmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['course', 'title', 'description', 'deadline', 'max_score', 'attachment']


class GradeSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['score', 'feedback']
