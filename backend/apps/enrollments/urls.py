from django.urls import path
from . import views

urlpatterns = [
    path('enroll/', views.EnrollView.as_view(), name='enroll'),
    path('my/', views.MyEnrollmentsView.as_view(), name='my-enrollments'),
    path('<int:course_id>/unenroll/', views.UnenrollView.as_view(), name='unenroll'),
    path('admin/all/', views.AdminEnrollmentListView.as_view(), name='admin-enrollments'),
]
