from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Lesson, LessonProgress
from .serializers import (
    LessonListSerializer, LessonDetailSerializer,
    LessonCreateUpdateSerializer, LessonProgressSerializer
)
from apps.users.permissions import IsAdminOrInstructor
from apps.enrollments.models import Enrollment


class LessonDetailView(generics.RetrieveAPIView):
    serializer_class = LessonDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Lesson.objects.select_related('chapter__course')

    def retrieve(self, request, *args, **kwargs):
        lesson = self.get_object()
        course = lesson.chapter.course

        # Check access: preview lessons or enrolled students
        if not lesson.is_preview:
            is_enrolled = Enrollment.objects.filter(
                student=request.user, course=course
            ).exists()
            is_owner = course.instructor == request.user
            is_admin = request.user.role == 'admin'
            if not (is_enrolled or is_owner or is_admin):
                return Response({'error': 'Bạn chưa đăng ký khóa học này.'}, status=403)

        serializer = self.get_serializer(lesson, context={'request': request})
        return Response(serializer.data)


class LessonCreateView(generics.CreateAPIView):
    serializer_class = LessonCreateUpdateSerializer
    permission_classes = [IsAdminOrInstructor]


class LessonUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LessonCreateUpdateSerializer
    permission_classes = [IsAdminOrInstructor]
    queryset = Lesson.objects.all()


class UpdateLessonProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(pk=lesson_id)
        except Lesson.DoesNotExist:
            return Response({'error': 'Bài học không tồn tại.'}, status=404)

        watch_percentage = request.data.get('watch_percentage', 0)
        progress, created = LessonProgress.objects.get_or_create(
            student=request.user,
            lesson=lesson
        )
        progress.watch_percentage = max(progress.watch_percentage, int(watch_percentage))
        progress.is_completed = progress.watch_percentage >= 90
        progress.save()

        # Update enrollment progress
        self._update_enrollment_progress(request.user, lesson.chapter.course)

        return Response({
            'watch_percentage': progress.watch_percentage,
            'is_completed': progress.is_completed
        })

    def _update_enrollment_progress(self, user, course):
        try:
            enrollment = Enrollment.objects.get(student=user, course=course)
            total_lessons = Lesson.objects.filter(chapter__course=course).count()
            if total_lessons == 0:
                return
            completed = LessonProgress.objects.filter(
                student=user, lesson__chapter__course=course, is_completed=True
            ).count()
            enrollment.progress = int((completed / total_lessons) * 100)
            enrollment.save()
        except Enrollment.DoesNotExist:
            pass
