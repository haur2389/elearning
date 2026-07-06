"""
Chatbot tư vấn khóa học — gọi Groq AI (api.groq.com, OpenAI-compatible).

Endpoint: POST /api/ai/chat/
Request:  { "message": str, "history": [{"role": "user"|"assistant", "content": str}, ...],
            "current_course_id": int|null }
Response: { "reply": str, "courses": [ {id, title, price, level, duration_hours, instructor} ]|null,
            "handoff": bool }

Cấu hình qua biến môi trường (đã có sẵn trong core/settings.py):
    GROQ_API_KEY, GROQ_MODEL, SUPPORT_EMAIL, SUPPORT_HOTLINE
"""
import json
import requests

from django.conf import settings
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.courses.models import Course

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"

# Từ khoá cho thấy người dùng muốn nói chuyện với người thật
HANDOFF_KEYWORDS = [
    "nhân viên", "tư vấn viên", "người thật", "gặp ai đó",
    "hotline", "liên hệ trực tiếp", "gọi điện", "khiếu nại",
    "hoàn tiền", "báo lỗi thanh toán", "không hài lòng",
]


class AIChatView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        message = (request.data.get("message") or "").strip()
        history = request.data.get("history") or []
        current_course_id = request.data.get("current_course_id")

        if not message:
            return Response({"reply": "Bạn muốn hỏi gì về khóa học nào? 😊", "courses": None, "handoff": False})

        if not settings.GROQ_API_KEY:
            return Response({
                "reply": "Trợ lý AI hiện chưa được cấu hình (thiếu GROQ_API_KEY). "
                         "Vui lòng liên hệ hỗ trợ để được tư vấn trực tiếp.",
                "courses": None,
                "handoff": True,
            })

        # 1) Tìm khoá học liên quan trong DB để cho AI ngữ cảnh thật
        matched_courses = self._search_courses(message)
        current_course = None
        if current_course_id:
            current_course = Course.objects.filter(pk=current_course_id, status="published").first()

        # 2) Build system prompt kèm dữ liệu khóa học thật
        system_prompt = self._build_system_prompt(matched_courses, current_course)

        # 3) Gọi Groq
        messages = [{"role": "system", "content": system_prompt}]
        for h in history[-10:]:
            role = h.get("role")
            content = h.get("content")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": message})

        try:
            resp = requests.post(
                GROQ_CHAT_URL,
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.GROQ_MODEL,
                    "messages": messages,
                    "temperature": 0.6,
                    "max_tokens": 700,
                },
                timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
            reply = data["choices"][0]["message"]["content"].strip()
        except Exception:
            return Response({
                "reply": "Xin lỗi, trợ lý AI đang gặp sự cố kết nối. Vui lòng thử lại sau ít phút, "
                         f"hoặc liên hệ {settings.SUPPORT_EMAIL} / {settings.SUPPORT_HOTLINE}.",
                "courses": None,
                "handoff": True,
            })

        handoff = self._needs_handoff(message, reply)
        courses_payload = self._serialize_courses(matched_courses) if matched_courses else None

        return Response({"reply": reply, "courses": courses_payload, "handoff": handoff})

    # ── Helpers ──────────────────────────────────────────────────────
    def _search_courses(self, message, limit=3):
        qs = Course.objects.filter(status="published")

        lowered = message.lower()
        if "miễn phí" in lowered or "free" in lowered:
            qs = qs.filter(price=0)
        if "cơ bản" in lowered or "beginner" in lowered:
            qs = qs.filter(level="beginner")
        elif "trung cấp" in lowered or "intermediate" in lowered:
            qs = qs.filter(level="intermediate")
        elif "nâng cao" in lowered or "advanced" in lowered:
            qs = qs.filter(level="advanced")

        # Tìm theo từ khóa trong tiêu đề / mô tả / danh mục
        keywords = [w for w in message.split() if len(w) > 2]
        if keywords:
            keyword_q = Q()
            for w in keywords:
                keyword_q |= Q(title__icontains=w) | Q(category__name__icontains=w)
            text_matches = qs.filter(keyword_q)
            if text_matches.exists():
                qs = text_matches

        return list(qs.select_related("instructor", "category")[:limit])

    def _serialize_courses(self, courses):
        return [
            {
                "id": c.id,
                "title": c.title,
                "price": str(c.price),
                "level": c.level,
                "duration_hours": c.duration_hours,
                "instructor": c.instructor.full_name if c.instructor else "",
            }
            for c in courses
        ]

    def _build_system_prompt(self, matched_courses, current_course):
        lines = [
            "Bạn là trợ lý AI tư vấn tuyển sinh của Smart E-Learning, nói tiếng Việt, "
            "thân thiện, ngắn gọn, dùng emoji vừa phải.",
            "Chỉ tư vấn dựa trên danh sách khóa học thật bên dưới, không bịa thông tin.",
            "Nếu người dùng hỏi điều nằm ngoài khả năng (khiếu nại, hoàn tiền, sự cố thanh toán, "
            "muốn gặp người thật), hãy nói rõ bạn sẽ chuyển tiếp cho nhân viên hỗ trợ.",
        ]

        if current_course:
            lines.append(
                f"Người dùng đang xem trang chi tiết khóa học: '{current_course.title}' "
                f"(giá {current_course.price}, trình độ {current_course.level})."
            )

        if matched_courses:
            lines.append("Danh sách khóa học liên quan tìm được trong hệ thống:")
            for c in matched_courses:
                price = "Miễn phí" if float(c.price) == 0 else f"{c.price}đ"
                lines.append(f"- {c.title} | {price} | trình độ: {c.level} | {c.duration_hours}h")
        else:
            lines.append("Không tìm thấy khóa học nào khớp trực tiếp với câu hỏi hiện tại trong hệ thống.")

        return "\n".join(lines)

    def _needs_handoff(self, message, reply):
        lowered = (message + " " + reply).lower()
        return any(kw in lowered for kw in HANDOFF_KEYWORDS)
