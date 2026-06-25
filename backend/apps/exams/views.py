from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Exam, Question, ExamResult
from .serializers import (
    ExamListSerializer, ExamDetailSerializer, ExamCreateSerializer,
    QuestionAdminSerializer, SubmitExamSerializer, ExamResultSerializer
)
from apps.users.permissions import IsAdminOrInstructor, IsAdmin
from apps.enrollments.models import Enrollment


class ExamListView(generics.ListAPIView):
    serializer_class = ExamListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        qs = Exam.objects.filter(course_id=course_id, is_active=True)
        # Nếu chưa có đề thi, tự động tạo
        if not qs.exists():
            try:
                from apps.courses.models import Course
                from django.core.management import call_command
                course = Course.objects.get(pk=course_id)
                call_command('seed_exams', course_id=int(course_id), verbosity=0)
                qs = Exam.objects.filter(course_id=course_id, is_active=True)
            except Exception:
                pass
        return qs


class ExamDetailView(generics.RetrieveAPIView):
    serializer_class = ExamDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Exam.objects.all()

    def retrieve(self, request, *args, **kwargs):
        exam = self.get_object()
        # Check enrollment
        is_enrolled = Enrollment.objects.filter(student=request.user, course=exam.course).exists()
        is_staff = request.user.role in ['admin', 'instructor']
        if not (is_enrolled or is_staff):
            return Response({'error': 'Bạn chưa đăng ký khóa học này.'}, status=403)
        return super().retrieve(request, *args, **kwargs)


class ExamCreateView(generics.CreateAPIView):
    serializer_class = ExamCreateSerializer
    permission_classes = [IsAdminOrInstructor]


class ExamUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExamCreateSerializer
    permission_classes = [IsAdminOrInstructor]
    queryset = Exam.objects.all()


class QuestionCreateView(generics.CreateAPIView):
    serializer_class = QuestionAdminSerializer
    permission_classes = [IsAdminOrInstructor]


class QuestionUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionAdminSerializer
    permission_classes = [IsAdminOrInstructor]
    queryset = Question.objects.all()


class SubmitExamView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, exam_id):
        try:
            exam = Exam.objects.get(pk=exam_id, is_active=True)
        except Exam.DoesNotExist:
            return Response({'error': 'Đề thi không tồn tại.'}, status=404)

        serializer = SubmitExamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        answers = serializer.validated_data['answers']
        time_spent = serializer.validated_data['time_spent']

        # Grade exam
        questions = exam.questions.all()
        total_points = sum(q.points for q in questions)
        earned_points = 0
        detailed_answers = {}

        for question in questions:
            q_id = str(question.id)
            student_answer = answers.get(q_id, '').strip().lower()
            correct = question.correct_answer.strip().lower()
            is_correct = student_answer == correct

            if is_correct:
                earned_points += question.points

            detailed_answers[q_id] = {
                'student_answer': answers.get(q_id, ''),
                'correct_answer': question.correct_answer,
                'is_correct': is_correct,
                'points': question.points if is_correct else 0
            }

        score = (earned_points / total_points * 100) if total_points > 0 else 0
        is_passed = score >= exam.pass_score

        result = ExamResult.objects.create(
            student=request.user,
            exam=exam,
            score=round(score, 2),
            total_points=total_points,
            earned_points=earned_points,
            is_passed=is_passed,
            answers=detailed_answers,
            submitted_at=timezone.now(),
            time_spent=time_spent
        )

        return Response({
            'message': 'Nộp bài thành công!',
            'result': ExamResultSerializer(result).data
        }, status=201)


class MyExamResultsView(generics.ListAPIView):
    serializer_class = ExamResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ExamResult.objects.filter(
            student=self.request.user
        ).select_related('exam').order_by('-submitted_at')


class ExamResultsAdminView(generics.ListAPIView):
    serializer_class = ExamResultSerializer
    permission_classes = [IsAdminOrInstructor]

    def get_queryset(self):
        exam_id = self.kwargs.get('exam_id')
        return ExamResult.objects.filter(exam_id=exam_id).select_related('student', 'exam')
