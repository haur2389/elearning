from django.urls import path
from . import views

urlpatterns = [
    path('courses/<int:course_id>/', views.ForumPostListView.as_view(), name='forum-list'),
    path('posts/<int:pk>/', views.ForumPostDetailView.as_view(), name='forum-post-detail'),
    path('replies/create/', views.ForumReplyCreateView.as_view(), name='forum-reply-create'),
    path('replies/<int:pk>/', views.ForumReplyDetailView.as_view(), name='forum-reply-detail'),
    path('replies/<int:pk>/solution/', views.MarkSolutionView.as_view(), name='mark-solution'),
]
