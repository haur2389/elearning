from rest_framework import serializers, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'course', 'student_name', 'student_avatar',
                  'rating', 'comment', 'created_at']
        read_only_fields = ['created_at']

    def get_student_avatar(self, obj):
        if obj.student.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.student.avatar.url)
        return None

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Đánh giá phải từ 1 đến 5 sao.")
        return value

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        review, _ = Review.objects.update_or_create(
            course=validated_data['course'],
            student=validated_data['student'],
            defaults={'rating': validated_data['rating'], 'comment': validated_data.get('comment', '')}
        )
        return review
