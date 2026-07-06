from django.urls import path
from .ai_views import AIChatView

urlpatterns = [
    path('chat/', AIChatView.as_view(), name='ai-chat'),
]
