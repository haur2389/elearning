from rest_framework import serializers
from .models import Exam, Question, ExamResult


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'content', 'question_type', 'option_a', 'option_b',
                  'option_c', 'option_d', 'points', 'order']
        # correct_answer excluded for students taking exam


class QuestionAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class ExamListSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()
    my_best_score = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = ['id', 'title', 'description', 'duration_minutes',
                  'total_questions', 'pass_score', 'is_active', 'question_count', 'my_best_score']

    def get_question_count(self, obj):
        return obj.questions.count()

    def get_my_best_score(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            results = ExamResult.objects.filter(student=request.user, exam=obj)
            if results.exists():
                return results.order_by('-score').first().score
        return None


class ExamDetailSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = ['id', 'title', 'description', 'duration_minutes',
                  'total_questions', 'pass_score', 'is_random', 'questions']

    def get_questions(self, obj):
        import random
        questions = list(obj.questions.all())
        if obj.is_random:
            random.shuffle(questions)
        questions = questions[:obj.total_questions]
        return QuestionSerializer(questions, many=True).data


class ExamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['course', 'title', 'description', 'duration_minutes',
                  'total_questions', 'pass_score', 'is_random', 'is_active']


class SubmitExamSerializer(serializers.Serializer):
    answers = serializers.DictField(
        child=serializers.CharField(allow_blank=True),
        help_text='{"question_id": "answer"}'
    )
    time_spent = serializers.IntegerField(default=0)


class ExamResultSerializer(serializers.ModelSerializer):
    exam_title = serializers.CharField(source='exam.title', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)

    class Meta:
        model = ExamResult
        fields = ['id', 'exam_title', 'student_name', 'student_email', 'score', 'total_points',
                  'earned_points', 'is_passed', 'answers', 'started_at', 'submitted_at', 'time_spent']
