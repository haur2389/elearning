from django.urls import path
from . import views

urlpatterns = [
    path('courses/<int:course_id>/', views.AssignmentListView.as_view(), name='assignment-list'),
    path('create/', views.AssignmentCreateView.as_view(), name='assignment-create'),
    path('<int:pk>/', views.AssignmentDetailView.as_view(), name='assignment-detail'),
    path('<int:assignment_id>/submit/', views.SubmitAssignmentView.as_view(), name='assignment-submit'),
    path('<int:assignment_id>/submissions/', views.AssignmentSubmissionsView.as_view(), name='assignment-submissions'),
    path('submissions/<int:submission_id>/grade/', views.GradeSubmissionView.as_view(), name='grade-submission'),
    path('my-submissions/', views.MySubmissionsView.as_view(), name='my-submissions'),
]
