from rest_framework import serializers
from .models import Category, Course, Chapter
from apps.users.serializers import UserProfileSerializer


class CategorySerializer(serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'course_count']

    def get_course_count(self, obj):
        return obj.courses.filter(status='published').count()


class ChapterSerializer(serializers.ModelSerializer):
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = ['id', 'title', 'order', 'lesson_count']

    def get_lesson_count(self, obj):
        return obj.lessons.count()


class ChapterDetailSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = ['id', 'title', 'order', 'lessons']

    def get_lessons(self, obj):
        from apps.lessons.serializers import LessonListSerializer
        return LessonListSerializer(obj.lessons.all(), many=True).data


class CourseListSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    avg_rating = serializers.FloatField(read_only=True)
    total_students = serializers.IntegerField(read_only=True)
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'thumbnail_url',
            'price', 'level', 'status', 'instructor_name', 'category_name',
            'avg_rating', 'total_students', 'duration_hours', 'created_at'
        ]

    def get_thumbnail_url(self, obj):
        if not obj.thumbnail:
            return None
        thumb = str(obj.thumbnail)
        # Nếu là URL đầy đủ thì trả về thẳng
        if thumb.startswith('http://') or thumb.startswith('https://'):
            return thumb
        # Nếu là đường dẫn tương đối
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri('/' + thumb.lstrip('/'))
        return thumb


class CourseDetailSerializer(serializers.ModelSerializer):
    instructor = UserProfileSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    chapters = ChapterDetailSerializer(many=True, read_only=True)
    avg_rating = serializers.FloatField(read_only=True)
    total_students = serializers.IntegerField(read_only=True)
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'thumbnail',
            'price', 'level', 'status', 'requirements', 'objectives',
            'instructor', 'category', 'chapters',
            'avg_rating', 'total_students', 'duration_hours',
            'is_enrolled', 'created_at'
        ]

    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.enrollments.filter(student=request.user).exists()
        return False


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'title', 'description', 'category', 'thumbnail',
            'price', 'level', 'status', 'duration_hours',
            'requirements', 'objectives'
        ]

    def create(self, validated_data):
        validated_data['instructor'] = self.context['request'].user
        return super().create(validated_data)
