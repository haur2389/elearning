from django.urls import path
from . import views

urlpatterns = [
    # Enrollment
    path('enroll/', views.EnrollView.as_view(), name='enroll'),
    path('my/', views.MyEnrollmentsView.as_view(), name='my-enrollments'),
    path('<int:course_id>/unenroll/', views.UnenrollView.as_view(), name='unenroll'),
    path('admin/all/', views.AdminEnrollmentListView.as_view(), name='admin-enrollments'),

    # Payment
    path('payments/my/', views.MyPaymentsView.as_view(), name='my-payments'),
    path('payments/admin/', views.AdminPaymentListView.as_view(), name='admin-payments'),
    path('payments/<int:pk>/update/', views.AdminPaymentUpdateView.as_view(), name='admin-payment-update'),

    # Certificate
    path('certificates/my/', views.MyCertificatesView.as_view(), name='my-certificates'),
    path('certificates/issue/', views.IssueCertificateView.as_view(), name='issue-certificate'),
    path('certificates/admin/', views.AdminCertificateListView.as_view(), name='admin-certificates'),
]
