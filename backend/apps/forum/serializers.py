from rest_framework import serializers, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ForumPost, ForumReply


class ForumReplySerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    author_role = serializers.CharField(source='author.role', read_only=True)
    author_avatar = serializers.SerializerMethodField()

    class Meta:
        model = ForumReply
        fields = ['id', 'author_name', 'author_role', 'author_avatar',
                  'content', 'is_solution', 'created_at']

    def get_author_avatar(self, obj):
        if obj.author.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.author.avatar.url)
        return None


class ForumPostListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = ForumPost
        fields = ['id', 'title', 'content', 'author_name',
                  'is_pinned', 'reply_count', 'created_at']

    def get_reply_count(self, obj):
        return obj.replies.count()


class ForumPostDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    replies = ForumReplySerializer(many=True, read_only=True)

    class Meta:
        model = ForumPost
        fields = ['id', 'title', 'content', 'author_name',
                  'is_pinned', 'replies', 'created_at']


class ForumPostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForumPost
        fields = ['course', 'title', 'content']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class ForumReplyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForumReply
        fields = ['post', 'content']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
