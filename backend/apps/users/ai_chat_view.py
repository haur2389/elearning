"""
AI Chat View — Tư vấn đăng ký môn học bằng Claude AI
Endpoint: POST /api/ai/chat/
"""
import re
import json
import urllib.request
import urllib.error
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.conf import settings


# ── LẤY DỮ LIỆU THẬT TỪ DATABASE ────────────────────────────────────
def get_db_context():
    """Query database, trả về dict chứa toàn bộ data cần thiết cho AI"""
    try:
        from apps.courses.models import Course, Category
        from apps.users.models import User
        from apps.exams.models import Exam
        from apps.enrollments.models import Enrollment
        from apps.assignments.models import Assignment

        categories = list(Category.objects.all().values('id', 'name', 'description'))

        courses = list(
            Course.objects.filter(status='published')
            .select_related('instructor', 'category')
            .values(
                'id', 'title', 'description', 'level', 'price',
                'duration_hours', 'requirements', 'objectives',
                'instructor__full_name', 'category__name',
            )
        )

        exams = list(
            Exam.objects.filter(is_active=True)
            .select_related('course')
            .values('title', 'course__title', 'duration_minutes', 'pass_score', 'total_questions')
        )

        stats = {
            'total_students':     User.objects.filter(role='student').count(),
            'total_instructors':  User.objects.filter(role='instructor').count(),
            'total_enrollments':  Enrollment.objects.count(),
            'total_assignments':  Assignment.objects.count(),
        }

        return {
            'categories': categories,
            'courses':    courses,
            'exams':      exams,
            'stats':      stats,
        }
    except Exception:
        return None


# ── XÂY DỰNG SYSTEM PROMPT CHO CLAUDE ────────────────────────────────
LEVEL_MAP = {
    'beginner':     'Cơ bản',
    'intermediate': 'Trung cấp',
    'advanced':     'Nâng cao',
}

def build_system_prompt(db):
    """Tạo system prompt chứa toàn bộ context database thực"""

    # Courses text cho prompt
    courses_text = ""
    all_courses_serialized = []

    if db and db.get('courses'):
        for c in db['courses']:
            price_val = float(str(c['price'] or 0))
            price_str = "Miễn phí" if price_val == 0 else f"{int(price_val):,}đ"
            level_str = LEVEL_MAP.get(c.get('level', ''), c.get('level', ''))
            inst      = c.get('instructor__full_name') or 'N/A'
            cat       = c.get('category__name') or 'Chung'
            hours     = c.get('duration_hours', 0)

            courses_text += (
                f"  [ID:{c['id']}] {c['title']} | {cat} | {level_str} | "
                f"{price_str} | {hours}h | GV: {inst}\n"
            )
            all_courses_serialized.append({
                'id':            c['id'],
                'title':         c['title'],
                'price':         str(c['price'] or '0'),
                'level':         c.get('level', ''),
                'duration_hours': c.get('duration_hours', 0),
                'category':      cat,
                'instructor':    inst,
            })

    # Categories text
    cats_text = ""
    if db and db.get('categories'):
        for cat in db['categories']:
            cats_text += f"  - {cat['name']}"
            if cat.get('description'):
                cats_text += f": {cat['description']}"
            cats_text += "\n"

    # Exams text
    exams_text = ""
    if db and db.get('exams'):
        for e in db['exams'][:20]:
            exams_text += (
                f"  - {e['title']} (Môn: {e.get('course__title','?')} | "
                f"{e['duration_minutes']} phút | {e['total_questions']} câu | "
                f"Đạt: {e['pass_score']}%)\n"
            )

    stats = db.get('stats', {}) if db else {}

    system_prompt = f"""Bạn là trợ lý AI tư vấn học tập của hệ thống **Smart E-Learning** - nền tảng học trực tuyến của Đại học Bình Dương.

Nhiệm vụ chính của bạn: Giúp sinh viên **tìm và đăng ký môn học phù hợp**.

═══════════════════════════════════════
DỮ LIỆU HỆ THỐNG (CẬP NHẬT THỜI GIAN THỰC)
═══════════════════════════════════════

📊 THỐNG KÊ:
  - Sinh viên: {stats.get('total_students', 0)} người
  - Giảng viên: {stats.get('total_instructors', 0)} người
  - Lượt đăng ký: {stats.get('total_enrollments', 0)}
  - Bài tập: {stats.get('total_assignments', 0)}

🏷️ DANH MỤC:
{cats_text or "  (Chưa có danh mục)"}

📚 KHÓA HỌC ĐANG MỞ ({len(db['courses']) if db and db.get('courses') else 0} khóa):
{courses_text or "  (Chưa có khóa học nào được công bố)"}

📝 KỲ THI ({len(db['exams']) if db and db.get('exams') else 0} đề):
{exams_text or "  (Chưa có kỳ thi)"}

═══════════════════════════════════════
HƯỚNG DẪN TRẢ LỜI
═══════════════════════════════════════

✅ CHỈ tư vấn dựa trên dữ liệu THẬT ở trên - KHÔNG bịa đặt khóa học hay thông tin.

✅ LUÔN trả lời bằng tiếng Việt, thân thiện, ngắn gọn (tối đa 5-6 dòng/câu).

✅ KHI gợi ý khóa học cụ thể: thêm [COURSES:id1,id2,...] ở CUỐI tin nhắn.
   Ví dụ: "Tôi gợi ý bạn khóa học ABC và XYZ! [COURSES:3,7]"

✅ LUÔN kết thúc bằng câu hỏi mở hoặc hành động tiếp theo.

✅ CÁC TÌNH HUỐNG THƯỜNG GẶP:
   - Hỏi "có khóa X không?" → Tìm trong danh sách, trả lời cụ thể + [COURSES:id]
   - Hỏi "muốn học lập trình" → Hỏi thêm trình độ, mục tiêu rồi gợi ý
   - Hỏi "học phí bao nhiêu" → Liệt kê ngắn gọn theo từng mức giá
   - Hỏi "cách đăng ký" → Hướng dẫn: Chọn khóa → Nhấn Đăng ký → Thanh toán
   - Hỏi "chứng chỉ" → Giải thích: Hoàn thành 100% + đạt 70% điểm → cấp chứng chỉ PDF

❌ KHÔNG: bịa thông tin, trả lời dài dòng, dùng tiếng Anh (trừ tên kỹ thuật).
"""
    return system_prompt, all_courses_serialized


# ── GỌI ANTHROPIC API ─────────────────────────────────────────────────
def call_claude(system_prompt, messages, api_key):
    """Gọi Claude Haiku API, trả về text hoặc raise Exception"""
    payload = json.dumps({
        'model':      'claude-haiku-4-5-20251001',
        'max_tokens': 600,
        'system':     system_prompt,
        'messages':   messages,
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.anthropic.com/v1/messages',
        data=payload,
        headers={
            'x-api-key':         api_key,
            'anthropic-version': '2023-06-01',
            'content-type':      'application/json',
        },
        method='POST',
    )

    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        return data['content'][0]['text']


# ── PARSE COURSE IDS TỪ RESPONSE ─────────────────────────────────────
def extract_course_ids(text):
    """Lấy [COURSES:1,2,3] từ text AI, trả về (clean_text, [ids])"""
    match = re.search(r'\[COURSES:([\d,\s]+)\]', text)
    if not match:
        return text, []
    ids = [int(x.strip()) for x in match.group(1).split(',') if x.strip().isdigit()]
    clean = re.sub(r'\s*\[COURSES:[\d,\s]+\]', '', text).strip()
    return clean, ids


# ── FALLBACK KHI CHƯA CÓ API KEY ─────────────────────────────────────
def fallback_response(message, db):
    """Dùng logic FAQ tĩnh cũ, không cần API key"""
    try:
        from apps.users.ai_views import find_best_answer, normalize
        answer = find_best_answer(message, db)
        if answer:
            return answer
    except Exception:
        pass

    return (
        "Xin lỗi, tôi chưa tìm được câu trả lời phù hợp. 🙏\n\n"
        "Bạn thử hỏi:\n"
        "📚 Tên khóa học cụ thể (VD: 'có khóa Python không?')\n"
        "💰 Học phí (VD: 'khóa học miễn phí')\n"
        "📝 Cách đăng ký môn học\n\n"
        "Hoặc liên hệ hỗ trợ trực tiếp! 😊"
    )


# ── MAIN VIEW ─────────────────────────────────────────────────────────
class AIChatView(APIView):
    """
    POST /api/ai/chat/
    Body: { "message": "...", "history": [...] }
    Return: { "reply": "...", "courses": [...] }  (courses là optional)
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        message = request.data.get('message', '').strip()
        history = request.data.get('history', [])  # Lịch sử hội thoại (tối đa 10 tin)

        if not message:
            return Response({'reply': 'Vui lòng nhập câu hỏi!'})

        # Lấy dữ liệu DB - query mới mỗi lần, không cache
        db = get_db_context()

        # Lấy API key từ settings (đọc từ .env)
        api_key = getattr(settings, 'ANTHROPIC_API_KEY', '').strip()

        # ─ Nếu chưa có API key → fallback sang FAQ tĩnh ─
        if not api_key:
            reply = fallback_response(message, db)
            return Response({'reply': reply})

        # ─ Có API key → dùng Claude AI ─
        system_prompt, all_courses = build_system_prompt(db)

        # Xây dựng history (tối đa 10 tin nhắn gần nhất để tiết kiệm token)
        messages = []
        for h in history[-10:]:
            role    = h.get('role', '')
            content = h.get('content', '')
            if role in ('user', 'assistant') and content:
                messages.append({'role': role, 'content': content})
        messages.append({'role': 'user', 'content': message})

        try:
            reply_raw = call_claude(system_prompt, messages, api_key)
        except urllib.error.HTTPError as e:
            # Log chi tiết lỗi HTTP (401 = key sai, 429 = rate limit, v.v.)
            err_body = e.read().decode('utf-8') if hasattr(e, 'read') else ''
            if e.code == 401:
                reply = fallback_response(message, db)
            elif e.code == 429:
                reply = "Trợ lý AI đang bận, vui lòng thử lại sau ít phút nhé! 🙏"
            else:
                reply = fallback_response(message, db)
            return Response({'reply': reply})
        except Exception:
            reply = fallback_response(message, db)
            return Response({'reply': reply})

        # Parse [COURSES:...] tag nếu AI trả về
        reply_clean, course_ids = extract_course_ids(reply_raw)

        result = {'reply': reply_clean}
        if course_ids:
            matched = [c for c in all_courses if c['id'] in course_ids]
            if matched:
                result['courses'] = matched

        return Response(result)
