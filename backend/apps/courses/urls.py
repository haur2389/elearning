from django.urls import path
from . import views

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course-list'),
    path('create/', views.CourseCreateView.as_view(), name='course-create'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('<int:pk>/update/', views.CourseUpdateView.as_view(), name='course-update'),
    path('my-courses/', views.InstructorCourseListView.as_view(), name='my-courses'),
    path('<int:course_id>/chapters/', views.ChapterListCreateView.as_view(), name='chapter-list'),
    path('chapters/<int:pk>/', views.ChapterDetailView.as_view(), name='chapter-detail'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
]
