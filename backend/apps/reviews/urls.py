from django.urls import path
from . import views

urlpatterns = [
    path('courses/<int:course_id>/', views.ReviewListCreateView.as_view(), name='review-list'),
    path('<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review-delete'),
]
