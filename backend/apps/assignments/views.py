from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Assignment, Submission
from .serializers import AssignmentSerializer, AssignmentCreateSerializer, SubmissionSerializer, GradeSubmissionSerializer
from apps.users.permissions import IsAdminOrInstructor


class AssignmentListView(generics.ListAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # FIX: trả về array

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        return Assignment.objects.filter(course_id=course_id).order_by('-created_at')


class AssignmentCreateView(generics.CreateAPIView):
    serializer_class = AssignmentCreateSerializer
    permission_classes = [IsAdminOrInstructor]

    def perform_create(self, serializer):
        assignment = serializer.save()
        from apps.notifications.utils import notify_enrolled_students
        deadline_str = assignment.deadline.strftime('%d/%m/%Y %H:%M')
        notify_enrolled_students(
            assignment.course,
            title=f'Bài tập mới: {assignment.title}',
            message=f'Khóa học "{assignment.course.title}" vừa có bài tập mới: {assignment.title}. Hạn nộp: {deadline_str}',
            notif_type='new_assignment',
            link=f'/course-detail.html?id={assignment.course.id}',
        )


class AssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssignmentCreateSerializer
    permission_classes = [IsAdminOrInstructor]
    queryset = Assignment.objects.all()


class SubmitAssignmentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, assignment_id):
        try:
            assignment = Assignment.objects.get(pk=assignment_id)
        except Assignment.DoesNotExist:
            return Response({'error': 'Bài tập không tồn tại.'}, status=404)

        if Submission.objects.filter(assignment=assignment, student=request.user).exists():
            return Response({'error': 'Bạn đã nộp bài này rồi.'}, status=400)

        is_late = timezone.now() > assignment.deadline
        status_val = 'late' if is_late else 'submitted'

        submission = Submission.objects.create(
            assignment=assignment,
            student=request.user,
            file=request.FILES.get('file'),
            note=request.data.get('note', ''),
            status=status_val
        )

        from apps.notifications.utils import notify
        notify(
            assignment.course.instructor,
            title=f'Bài nộp mới: {assignment.title}',
            message=f'{request.user.full_name} vừa nộp bài tập "{assignment.title}"' + (' (nộp muộn)' if is_late else '') + '.',
            notif_type='new_submission',
            link='/instructor/assignments.html',
        )

        return Response({
            'message': 'Nộp bài thành công!' + (' (Nộp muộn)' if is_late else ''),
            'submission': SubmissionSerializer(submission).data
        }, status=201)


class GradeSubmissionView(APIView):
    permission_classes = [IsAdminOrInstructor]

    def patch(self, request, submission_id):
        try:
            submission = Submission.objects.get(pk=submission_id)
        except Submission.DoesNotExist:
            return Response({'error': 'Bài nộp không tồn tại.'}, status=404)

        serializer = GradeSubmissionSerializer(submission, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        submission = serializer.save(status='graded', graded_at=timezone.now())

        from apps.notifications.utils import notify
        notify(
            submission.student,
            title=f'Đã chấm điểm: {submission.assignment.title}',
            message=f'Bài tập "{submission.assignment.title}" của bạn đã được chấm: {submission.score} điểm.',
            notif_type='assignment_graded',
            link=f'/course-detail.html?id={submission.assignment.course_id}',
        )

        return Response({'message': 'Chấm điểm thành công!', 'submission': SubmissionSerializer(submission).data})


class MySubmissionsView(generics.ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Submission.objects.none()
        return Submission.objects.filter(student=self.request.user).order_by('-submitted_at')


class AssignmentSubmissionsView(generics.ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [IsAdminOrInstructor]
    pagination_class = None  # FIX: trả về array trực tiếp

    def get_queryset(self):
        return Submission.objects.filter(
            assignment_id=self.kwargs['assignment_id']
        ).select_related('student')
