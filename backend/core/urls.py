from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Smart E-Learning API",
        default_version='v1',
        description="API hệ thống học trực tuyến thông minh - ĐH Bình Dương",
        contact=openapi.Contact(email="support@elearning.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/auth/', include('apps.users.urls')),
    path('api/courses/', include('apps.courses.urls')),
    path('api/lessons/', include('apps.lessons.urls')),
    path('api/enrollments/', include('apps.enrollments.urls')),
    path('api/exams/', include('apps.exams.urls')),
    path('api/assignments/', include('apps.assignments.urls')),
    path('api/reviews/', include('apps.reviews.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/forum/', include('apps.forum.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)