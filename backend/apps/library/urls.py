from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookListView.as_view(), name='book-list'),
    path('categories/', views.BookCategoryListView.as_view(), name='book-categories'),
    path('admin/', views.AdminBookListCreateView.as_view(), name='admin-books'),
    path('admin/<int:pk>/', views.AdminBookDetailView.as_view(), name='admin-book-detail'),
    path('<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
]
