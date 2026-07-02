from django.urls import path
from .ai_chat_view import AIChatView

urlpatterns = [
    path('chat/', AIChatView.as_view(), name='ai-chat'),
]
