from django.urls import path
from . import views

urlpatterns = [
    path('courses/<int:course_id>/', views.ExamListView.as_view(), name='exam-list'),
    path('<int:pk>/', views.ExamDetailView.as_view(), name='exam-detail'),
    path('create/', views.ExamCreateView.as_view(), name='exam-create'),
    path('<int:pk>/update/', views.ExamUpdateView.as_view(), name='exam-update'),
    path('<int:exam_id>/questions/', views.ExamQuestionsAdminView.as_view(), name='exam-questions-admin'),
    path('<int:exam_id>/submit/', views.SubmitExamView.as_view(), name='exam-submit'),
    path('<int:exam_id>/results/', views.ExamResultsAdminView.as_view(), name='exam-results'),
    path('my-results/', views.MyExamResultsView.as_view(), name='my-exam-results'),
    path('questions/create/', views.QuestionCreateView.as_view(), name='question-create'),
    path('questions/<int:pk>/', views.QuestionUpdateView.as_view(), name='question-update'),
]
