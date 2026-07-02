from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/', views.LessonDetailView.as_view(), name='lesson-detail'),
    path('create/', views.LessonCreateView.as_view(), name='lesson-create'),
    path('<int:pk>/update/', views.LessonUpdateView.as_view(), name='lesson-update'),
    path('<int:lesson_id>/progress/', views.UpdateLessonProgressView.as_view(), name='lesson-progress'),
]
