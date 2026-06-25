import os
import json
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions


class AIChatView(APIView):
    permission_classes = [permissions.AllowAny]

    SYSTEM_PROMPT = """Bạn là AI trợ lý học tập thông minh của hệ thống Smart E-Learning - Đại học Bình Dương.
Bạn hỗ trợ sinh viên về TẤT CẢ các môn học CNTT: Lập trình Python/Java/C++, Cơ sở dữ liệu SQL, 
Lập trình Web (HTML/CSS/JavaScript/React), Trí tuệ nhân tạo & Machine Learning, 
Mạng máy tính, An toàn thông tin, Cấu trúc dữ liệu & Giải thuật, Hệ điều hành, 
Kỹ thuật phần mềm, và các chủ đề học tập khác.

Quy tắc trả lời:
- Trả lời bằng tiếng Việt, thân thiện, dễ hiểu
- Trả lời MỌI câu hỏi về học tập, kỹ thuật, CNTT - KHÔNG từ chối vô lý
- Giải thích rõ ràng, kèm ví dụ code khi phù hợp (dùng markdown code blocks)
- Với câu hỏi lập trình: đưa code mẫu chạy được
- Với câu hỏi tư vấn: hỏi thêm chi tiết để tư vấn chính xác
- Độ dài trả lời vừa phải (100-400 từ), không dài dòng
- Dùng emoji và markdown để dễ đọc hơn
- Nếu không biết thì nói thẳng và gợi ý nguồn tham khảo"""

    def post(self, request):
        message = request.data.get('message', '').strip()
        history = request.data.get('history', [])

        if not message:
            return Response({'reply': 'Vui lòng nhập câu hỏi!'})

        # Thử Claude API (Anthropic)
        anthropic_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if anthropic_key:
            try:
                reply = self._call_claude(message, history, anthropic_key)
                if reply:
                    return Response({'reply': reply})
            except Exception as e:
                pass

        # Thử Gemini API
        gemini_key = os.environ.get('GEMINI_API_KEY', '')
        if gemini_key:
            try:
                reply = self._call_gemini(message, history, gemini_key)
                if reply:
                    return Response({'reply': reply})
            except Exception as e:
                pass

        # Thử OpenAI API
        openai_key = os.environ.get('OPENAI_API_KEY', '')
        if openai_key:
            try:
                reply = self._call_openai(message, history, openai_key)
                if reply:
                    return Response({'reply': reply})
            except Exception as e:
                pass

        # Smart fallback
        reply = self._smart_reply(message)
        return Response({'reply': reply})

    def _call_claude(self, message, history, api_key):
        """Gọi Anthropic Claude API"""
        messages = []
        for h in history[-10:]:
            role = 'user' if h.get('role') == 'user' else 'assistant'
            messages.append({'role': role, 'content': h.get('content', '')})
        messages.append({'role': 'user', 'content': message})

        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json',
            },
            json={
                'model': 'claude-haiku-4-5-20251001',
                'max_tokens': 1024,
                'system': self.SYSTEM_PROMPT,
                'messages': messages,
            },
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            return data['content'][0]['text']
        return None

    def _call_gemini(self, message, history, api_key):
        """Gọi Google Gemini API"""
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=self.SYSTEM_PROMPT)

        chat_history = []
        for h in history[-8:]:
            role = 'user' if h.get('role') == 'user' else 'model'
            chat_history.append({'role': role, 'parts': [h.get('content', '')]})

        chat = model.start_chat(history=chat_history)
        response = chat.send_message(message)
        return response.text

    def _call_openai(self, message, history, api_key):
        """Gọi OpenAI ChatGPT API"""
        messages = [{'role': 'system', 'content': self.SYSTEM_PROMPT}]
        for h in history[-8:]:
            messages.append({'role': h.get('role', 'user'), 'content': h.get('content', '')})
        messages.append({'role': 'user', 'content': message})

        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
            json={'model': 'gpt-3.5-turbo', 'messages': messages, 'max_tokens': 800},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return None

    def _smart_reply(self, msg):
        """Fallback thông minh khi không có API key"""
        msg_lower = msg.lower()

        greetings = ['xin chào', 'hello', 'hi ', 'chào', 'helo', 'hey']
        if any(w in msg_lower for w in greetings):
            return ("Xin chào! 👋 Tôi là AI trợ lý học tập E-Learning.\n\n"
                    "Tôi có thể giúp bạn về:\n"
                    "💻 **Lập trình**: Python, Java, C++, JavaScript\n"
                    "🌐 **Lập trình Web**: HTML, CSS, React, Node.js\n"
                    "🗄️ **CSDL**: SQL, MySQL, PostgreSQL\n"
                    "🤖 **AI/ML**: Machine Learning, Deep Learning\n"
                    "🔒 **Bảo mật**: An toàn thông tin, mã hóa\n"
                    "📚 **Cấu trúc dữ liệu & Giải thuật**\n\n"
                    "Bạn cần hỏi gì không? 😊")

        if any(w in msg_lower for w in ['python', 'def ', 'vòng lặp', 'list', 'dict', 'class ']):
            if 'vòng lặp' in msg_lower or 'for' in msg_lower or 'while' in msg_lower:
                return ("**Vòng lặp trong Python:**\n\n```python\n# For loop - biết trước số lần lặp\nfor i in range(5):\n    print(i)  # 0,1,2,3,4\n\n# While loop - dựa vào điều kiện\nn = 0\nwhile n < 5:\n    print(n)\n    n += 1\n\n# Lặp qua danh sách\nmonhoc = ['Python', 'SQL', 'Web']\nfor mon in monhoc:\n    print(f'Học: {mon}')\n```\n\n💡 Dùng `for` khi biết số lần lặp, `while` khi không biết trước.")
            if 'hàm' in msg_lower or 'function' in msg_lower:
                return ("**Hàm (Function) trong Python:**\n\n```python\ndef tinh_tong(a, b=0):\n    \"\"\"Tính tổng 2 số, b mặc định = 0\"\"\"\n    return a + b\n\n# Gọi hàm\nprint(tinh_tong(3, 4))  # 7\nprint(tinh_tong(5))     # 5\n\n# Lambda function\nbinh_phuong = lambda x: x ** 2\nprint(binh_phuong(4))   # 16\n```\n\n💡 `def` để định nghĩa hàm, tham số có thể có giá trị mặc định.")
            return ("**Python cơ bản:**\n\n```python\n# Kiểu dữ liệu cơ bản\nso = 42\nchu_chuoi = 'Xin chào'\ndanh_sach = [1, 2, 3, 4, 5]\ntap_hop = {1, 2, 3}  # set - không trùng lặp\ntu_dien = {'ten': 'An', 'tuoi': 20}  # dict\n\n# Nhập/xuất\nten = input('Tên bạn là: ')\nprint(f'Xin chào, {ten}!')\n```\n\nBạn muốn hỏi cụ thể về phần nào của Python?")

        if any(w in msg_lower for w in ['sql', 'select', 'csdl', 'cơ sở dữ liệu', 'join', 'insert', 'update', 'delete']):
            return ("**SQL cơ bản:**\n\n```sql\n-- Tạo bảng\nCREATE TABLE sinh_vien (\n    id INT PRIMARY KEY AUTO_INCREMENT,\n    ten VARCHAR(100) NOT NULL,\n    email VARCHAR(100) UNIQUE\n);\n\n-- Thêm dữ liệu\nINSERT INTO sinh_vien (ten, email) VALUES ('An', 'an@ubd.edu.vn');\n\n-- Truy vấn\nSELECT * FROM sinh_vien WHERE ten LIKE '%An%';\n\n-- Kết hợp bảng\nSELECT sv.ten, kh.ten_khoa\nFROM sinh_vien sv\nINNER JOIN dang_ky dk ON sv.id = dk.sv_id\nINNER JOIN khoa_hoc kh ON dk.kh_id = kh.id;\n```\n\nBạn cần hỏi về lệnh SQL nào cụ thể?")

        if any(w in msg_lower for w in ['html', 'css', 'javascript', 'web', 'react', 'node']):
            return ("**Lập trình Web - 3 thành phần chính:**\n\n```html\n<!DOCTYPE html>\n<html lang=\"vi\">\n<head>\n    <style>\n        .nut { background: #3b82f6; color: white; padding: 8px 16px; border-radius: 8px; }\n        .nut:hover { background: #2563eb; cursor: pointer; }\n    </style>\n</head>\n<body>\n    <h1>Chào mừng!</h1>\n    <button class=\"nut\" onclick=\"chaoHoi()\">Click tôi</button>\n    <script>\n        function chaoHoi() {\n            alert('Xin chào từ JavaScript! 👋');\n        }\n    </script>\n</body>\n</html>\n```\n\n🏗 **HTML** = Cấu trúc | 🎨 **CSS** = Kiểu dáng | ⚡ **JS** = Tương tác\n\nBạn muốn hỏi về phần nào?")

        if any(w in msg_lower for w in ['cấu trúc dữ liệu', 'stack', 'queue', 'linked list', 'tree', 'graph', 'giải thuật', 'sort', 'search', 'big-o', 'big o']):
            return ("**Cấu trúc dữ liệu cơ bản:**\n\n```python\n# Stack - LIFO (vào sau ra trước)\nstack = []\nstack.append(1)   # push\nstack.append(2)\nstack.pop()       # pop -> 2\n\n# Queue - FIFO (vào trước ra trước)\nfrom collections import deque\nqueue = deque()\nqueue.append(1)       # enqueue\nqueue.popleft()       # dequeue -> 1\n\n# Linked List (đơn giản)\nclass Node:\n    def __init__(self, data):\n        self.data = data\n        self.next = None\n```\n\n**Big-O phổ biến:**\n- O(1): truy cập array\n- O(log n): tìm kiếm nhị phân\n- O(n): tìm kiếm tuyến tính\n- O(n²): bubble sort\n\nBạn muốn hỏi chi tiết về cấu trúc nào?")

        if any(w in msg_lower for w in ['machine learning', 'ai', 'trí tuệ nhân tạo', 'deep learning', 'neural', 'học máy']):
            return ("**Machine Learning cơ bản:**\n\n```python\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.linear_model import LinearRegression\nimport numpy as np\n\n# Tạo dữ liệu mẫu\nX = np.array([[1], [2], [3], [4], [5]])\ny = np.array([2, 4, 6, 8, 10])\n\n# Chia train/test\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)\n\n# Huấn luyện mô hình\nmodel = LinearRegression()\nmodel.fit(X_train, y_train)\n\n# Dự đoán\nprint(model.predict([[6]]))  # ~12\n```\n\n**3 loại học ML:**\n- 📊 Supervised: có nhãn (phân loại, hồi quy)\n- 🔍 Unsupervised: không nhãn (phân cụm)\n- 🎮 Reinforcement: học từ phần thưởng\n\nBạn muốn tìm hiểu phần nào?")

        # Câu hỏi chung
        return (f"Tôi nhận được câu hỏi của bạn về: **{msg[:80]}**\n\n"
                "⚠️ Hiện tại chatbot đang chạy ở chế độ offline (chưa có API key AI).\n\n"
                "Tôi có thể trả lời tốt về:\n"
                "- 🐍 Python, Java, C++\n"
                "- 🌐 HTML, CSS, JavaScript\n"
                "- 🗄️ SQL, Cơ sở dữ liệu\n"
                "- 🤖 AI/Machine Learning cơ bản\n"
                "- 📚 Cấu trúc dữ liệu & Giải thuật\n\n"
                "Hãy hỏi cụ thể hơn hoặc liên hệ giảng viên để được hỗ trợ tốt hơn!")
