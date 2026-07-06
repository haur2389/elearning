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
    pagination_class = None  # FIX: trả về array

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        # ── FIX: Bỏ seed_data tự động gây crash 500 ──
        return Exam.objects.filter(course_id=course_id, is_active=True)

    def list(self, request, *args, **kwargs):
        course_id = self.kwargs.get('course_id')
        user = request.user
        is_staff = user.role in ['admin', 'instructor']
        is_enrolled = Enrollment.objects.filter(
            student=user, course_id=course_id
        ).exists()

        queryset = self.get_queryset()
        # FIX: pass request context để serializer lấy được my_best_score
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        data = list(serializer.data)  # convert to mutable list

        for exam in data:
            exam['can_take'] = is_enrolled and not is_staff

        return Response(data)


class ExamDetailView(generics.RetrieveAPIView):
    serializer_class = ExamDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Exam.objects.all()

    def retrieve(self, request, *args, **kwargs):
        exam = self.get_object()
        is_enrolled = Enrollment.objects.filter(student=request.user, course=exam.course).exists()
        is_staff = request.user.role in ['admin', 'instructor']
        if not (is_enrolled or is_staff):
            return Response({'error': 'Bạn chưa đăng ký khóa học này.'}, status=403)
        return super().retrieve(request, *args, **kwargs)


class ExamCreateView(generics.CreateAPIView):
    serializer_class = ExamCreateSerializer
    permission_classes = [IsAdminOrInstructor]

    def perform_create(self, serializer):
        exam = serializer.save()
        from apps.notifications.utils import notify_enrolled_students
        notify_enrolled_students(
            exam.course,
            title=f'Đề thi mới: {exam.title}',
            message=f'Khóa học "{exam.course.title}" vừa có đề thi mới: {exam.title}',
            notif_type='new_exam',
            link=f'/exam.html?id={exam.id}',
        )


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


# ── FIX: endpoint riêng cho giảng viên xem/sửa đề thi — trả về đầy đủ câu hỏi
# kèm đáp án đúng (QuestionAdminSerializer), khác với ExamDetailSerializer dùng
# cho học viên (ẩn correct_answer). Trước đây giảng viên phải bấm "Làm bài thi"
# mới xem được câu hỏi, không đúng và không sửa được gì. ──
class ExamQuestionsAdminView(generics.ListAPIView):
    serializer_class = QuestionAdminSerializer
    permission_classes = [IsAdminOrInstructor]
    pagination_class = None

    def get_queryset(self):
        exam_id = self.kwargs.get('exam_id')
        return Question.objects.filter(exam_id=exam_id).order_by('order', 'id')


class SubmitExamView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, exam_id):
        if request.user.role in ['admin', 'instructor']:
            return Response({'error': 'Giảng viên không thể làm bài thi.'}, status=403)

        try:
            exam = Exam.objects.get(pk=exam_id, is_active=True)
        except Exam.DoesNotExist:
            return Response({'error': 'Đề thi không tồn tại.'}, status=404)

        is_enrolled = Enrollment.objects.filter(
            student=request.user, course=exam.course
        ).exists()
        if not is_enrolled:
            return Response({'error': 'Bạn chưa đăng ký khóa học này.'}, status=403)

        serializer = SubmitExamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        answers = serializer.validated_data['answers']
        time_spent = serializer.validated_data['time_spent']

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

        # Đề thi ở đây được chấm tự động ngay khi nộp (trắc nghiệm/đúng-sai/điền
        # khuyết so khớp đáp án đúng), nên có kết quả ngay lập tức:
        # 1) Báo cho học viên biết điểm/đạt hay chưa đạt.
        # 2) Báo cho giảng viên phụ trách khóa học biết có học viên vừa thi.
        from apps.notifications.utils import notify
        notify(
            request.user,
            title=f'Kết quả thi: {exam.title}',
            message=f'Bạn đạt {result.score}% ({"Đạt" if is_passed else "Chưa đạt"}) trong đề thi "{exam.title}".',
            notif_type='exam_result',
            link='/my-exams.html',
        )
        notify(
            exam.course.instructor,
            title=f'Học viên vừa thi: {exam.title}',
            message=f'{request.user.full_name} vừa hoàn thành đề thi "{exam.title}" với {result.score}% ({"Đạt" if is_passed else "Chưa đạt"}).',
            notif_type='exam_attempt',
            link=f'/instructor/exam-results.html?exam={exam.id}',
        )

        return Response({
            'message': 'Nộp bài thành công!',
            'result': ExamResultSerializer(result).data
        }, status=201)


class MyExamResultsView(generics.ListAPIView):
    serializer_class = ExamResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # FIX: trả về array trực tiếp

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ExamResult.objects.none()
        return ExamResult.objects.filter(
            student=self.request.user
        ).select_related('exam').order_by('-submitted_at')


class ExamResultsAdminView(generics.ListAPIView):
    serializer_class = ExamResultSerializer
    permission_classes = [IsAdminOrInstructor]
    pagination_class = None  # FIX: trả về array trực tiếp

    def get_queryset(self):
        exam_id = self.kwargs.get('exam_id')
        return ExamResult.objects.filter(exam_id=exam_id).select_related('student', 'exam')


# ── FIX: Trang "Điểm thi" của admin có bộ lọc "-- Tất cả đề thi --" nhưng
# trước đây không có API nào trả về TOÀN BỘ kết quả thi cùng lúc (chỉ có
# endpoint theo từng exam_id), nên khi không chọn đề thi cụ thể bảng luôn
# trống dù học viên đã thi và có điểm. Endpoint này trả về toàn bộ kết
# quả thi: admin xem tất cả, giảng viên chỉ xem kết quả các đề thi thuộc
# khóa học do mình phụ trách. ──
class AllExamResultsAdminView(generics.ListAPIView):
    serializer_class = ExamResultSerializer
    permission_classes = [IsAdminOrInstructor]
    pagination_class = None

    def get_queryset(self):
        qs = ExamResult.objects.select_related('student', 'exam', 'exam__course').order_by('-submitted_at')
        if self.request.user.role == 'instructor':
            qs = qs.filter(exam__course__instructor=self.request.user)
        return qs