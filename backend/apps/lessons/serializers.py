from rest_framework import serializers
from .models import Lesson, LessonProgress


class LessonListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content_type', 'duration', 'order', 'is_preview']


class LessonDetailSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'content_type', 'video_url', 'pdf_file',
            'slide_url', 'content', 'duration', 'order', 'is_preview', 'progress'
        ]

    def get_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                p = LessonProgress.objects.get(student=request.user, lesson=obj)
                return {'watch_percentage': p.watch_percentage, 'is_completed': p.is_completed}
            except LessonProgress.DoesNotExist:
                pass
        return {'watch_percentage': 0, 'is_completed': False}


class LessonCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            'chapter', 'title', 'content_type', 'video_url',
            'pdf_file', 'slide_url', 'content', 'duration', 'order', 'is_preview'
        ]


class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = ['lesson', 'watch_percentage', 'is_completed', 'last_watched']
        read_only_fields = ['last_watched']
