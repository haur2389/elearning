from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.users.models import User
from apps.courses.models import Category, Course, Chapter
from apps.lessons.models import Lesson
from apps.exams.models import Exam, Question
import uuid

# 1 tín chỉ = 750.000đ (ĐH Bình Dương)
TC = 750000

COURSES_DATA = [
    {
        "code": "INF0433", "title": "Nhập môn lập trình", "tc": 3,
        "category": "Lập trình", "price": 0,  # Miễn phí - môn bắt buộc đầu tiên
        "level": "beginner",
        "description": "Môn học INF0433 - 3 tín chỉ (60 tiết: 30LT + 30TH). Nhập môn lập trình với Python dành cho sinh viên năm 1 ngành CNTT ĐH Bình Dương.",
        "objectives": "Hiểu các khái niệm cơ bản về lập trình\nViết được chương trình Python giải quyết bài toán thực tế\nNắm vững cấu trúc điều kiện, vòng lặp, hàm",
        "requirements": "Không yêu cầu kinh nghiệm lập trình trước",
        "duration_hours": 60,
        "thumbnail": "https://images.unsplash.com/photo-1587620962725-abab19836100?w=800&h=400&fit=crop&auto=format",
        "chapters": [
            {"title": "Chương 1: Giới thiệu lập trình và Python", "lessons": [
                {"title": "Bài 1: Lập trình là gì? Tại sao học Python?", "video_url": "https://www.youtube.com/watch?v=rfscVS0vtbw", "duration": 20, "preview": True},
                {"title": "Bài 2: Cài đặt Python và VS Code", "video_url": "https://www.youtube.com/watch?v=YYXdXT2l-Gg", "duration": 15, "preview": True},
                {"title": "Bài 3: Chương trình đầu tiên - Hello World", "video_url": "https://www.youtube.com/watch?v=fWjsdhR3z3c", "duration": 12},
            ]},
            {"title": "Chương 2: Biến và kiểu dữ liệu", "lessons": [
                {"title": "Bài 4: Biến, hằng số và kiểu dữ liệu", "video_url": "https://www.youtube.com/watch?v=Z1Yd7upQsXY", "duration": 18},
                {"title": "Bài 5: Nhập xuất dữ liệu - input() và print()", "video_url": "https://www.youtube.com/watch?v=PkZNo7MFNFg", "duration": 14},
            ]},
            {"title": "Chương 3: Cấu trúc điều kiện và vòng lặp", "lessons": [
                {"title": "Bài 6: Câu lệnh if-elif-else", "video_url": "https://www.youtube.com/watch?v=DZwmZ8Usvnk", "duration": 16},
                {"title": "Bài 7: Vòng lặp for và while", "video_url": "https://www.youtube.com/watch?v=OnDr4J2UXSA", "duration": 20},
                {"title": "Bài 8: Hàm (Function) trong Python", "video_url": "https://www.youtube.com/watch?v=9Os0o3wzS_I", "duration": 22},
            ]},
        ],
        "questions": [
            {"content": "Trong Python, hàm nào dùng để nhận dữ liệu từ bàn phím?", "a": "print()", "b": "input()", "c": "scan()", "d": "read()", "ans": "b"},
            {"content": "Kết quả của lệnh print(3 + 4 * 2) là bao nhiêu?", "a": "14", "b": "11", "c": "10", "d": "7", "ans": "b"},
            {"content": "Để khai báo hàm trong Python ta dùng từ khóa nào?", "a": "function", "b": "func", "c": "def", "d": "void", "ans": "c"},
            {"content": "Vòng lặp for i in range(5) sẽ lặp bao nhiêu lần?", "a": "4", "b": "5", "c": "6", "d": "Vô hạn", "ans": "b"},
            {"content": "Kiểu dữ liệu nào lưu trữ chuỗi văn bản trong Python?", "a": "int", "b": "float", "c": "str", "d": "bool", "ans": "c"},
            {"content": "Python là ngôn ngữ lập trình biên dịch (compiled language).", "type": "true_false", "a": "True", "b": "False", "c": "", "d": "", "ans": "false"},
            {"content": "Comment trong Python bắt đầu bằng ký tự nào?", "a": "//", "b": "/*", "c": "#", "d": "--", "ans": "c"},
            {"content": "Kết quả của type(3.14) là gì?", "a": "<class 'int'>", "b": "<class 'float'>", "c": "<class 'str'>", "d": "<class 'double'>", "ans": "b"},
            {"content": "Hàm len() trong Python dùng để làm gì?", "a": "Tính tổng", "b": "Đếm số phần tử", "c": "Tìm max", "d": "In ra màn hình", "ans": "b"},
            {"content": "List trong Python được bao bởi ký tự nào?", "a": "{}", "b": "()", "c": "[]", "d": "<>", "ans": "c"},
        ]
    },
    {
        "code": "INF0073", "title": "Cấu trúc dữ liệu và giải thuật", "tc": 3,
        "category": "Lập trình", "price": 3 * TC,
        "level": "intermediate",
        "description": "Môn học INF0073 - 3 tín chỉ (60 tiết: 30LT + 30TH). Các cấu trúc dữ liệu cơ bản (Stack, Queue, Tree, Graph) và các giải thuật sắp xếp, tìm kiếm.",
        "objectives": "Nắm vững các cấu trúc dữ liệu Stack, Queue, Linked List, Tree\nCài đặt các giải thuật sắp xếp: Bubble, Quick, Merge Sort\nPhân tích độ phức tạp thuật toán Big-O",
        "requirements": "Đã học INF0433 - Nhập môn lập trình",
        "duration_hours": 60,
        "thumbnail": "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=800&h=400&fit=crop&auto=format",
        "chapters": [
            {"title": "Chương 1: Độ phức tạp thuật toán", "lessons": [
                {"title": "Bài 1: Big-O Notation - Phân tích độ phức tạp", "video_url": "https://www.youtube.com/watch?v=__vX2sjlpXU", "duration": 18, "preview": True},
                {"title": "Bài 2: Đệ quy (Recursion)", "video_url": "https://www.youtube.com/watch?v=IJDJ0kBx2LM", "duration": 20, "preview": True},
            ]},
            {"title": "Chương 2: Cấu trúc dữ liệu tuyến tính", "lessons": [
                {"title": "Bài 3: Stack (Ngăn xếp)", "video_url": "https://www.youtube.com/watch?v=F1F2imiOJfk", "duration": 16},
                {"title": "Bài 4: Queue (Hàng đợi)", "video_url": "https://www.youtube.com/watch?v=XuCbpw6Bj1U", "duration": 15},
                {"title": "Bài 5: Linked List (Danh sách liên kết)", "video_url": "https://www.youtube.com/watch?v=njTh_OwMljA", "duration": 22},
            ]},
            {"title": "Chương 3: Giải thuật sắp xếp", "lessons": [
                {"title": "Bài 6: Bubble Sort & Selection Sort", "video_url": "https://www.youtube.com/watch?v=xli_FI7CuzA", "duration": 18},
                {"title": "Bài 7: Quick Sort & Merge Sort", "video_url": "https://www.youtube.com/watch?v=Hoixgm4-P4M", "duration": 22},
            ]},
        ],
        "questions": [
            {"content": "Stack là cấu trúc dữ liệu hoạt động theo nguyên tắc nào?", "a": "FIFO", "b": "LIFO", "c": "Random", "d": "Priority", "ans": "b"},
            {"content": "Độ phức tạp của thuật toán Bubble Sort trong trường hợp xấu nhất là?", "a": "O(n)", "b": "O(n log n)", "c": "O(n²)", "d": "O(1)", "ans": "c"},
            {"content": "Quick Sort sử dụng chiến lược nào?", "a": "Greedy", "b": "Dynamic Programming", "c": "Divide and Conquer", "d": "Backtracking", "ans": "c"},
            {"content": "Linked List khác Array ở điểm nào?", "a": "Linked List nhanh hơn khi truy cập ngẫu nhiên", "b": "Linked List dùng con trỏ, không cần bộ nhớ liên tục", "c": "Linked List có kích thước cố định", "d": "Không có sự khác biệt", "ans": "b"},
            {"content": "Queue hoạt động theo nguyên tắc FIFO.", "type": "true_false", "a": "True", "b": "False", "c": "", "d": "", "ans": "true"},
            {"content": "Binary Search yêu cầu mảng phải như thế nào?", "a": "Không cần điều kiện", "b": "Đã được sắp xếp", "c": "Có kích thước chẵn", "d": "Chứa số nguyên", "ans": "b"},
            {"content": "Cây nhị phân tìm kiếm (BST) có tính chất gì?", "a": "Node trái < Node gốc < Node phải", "b": "Tất cả node đều bằng nhau", "c": "Node trái > Node gốc", "d": "Không có quy tắc", "ans": "a"},
            {"content": "Merge Sort có độ phức tạp thời gian là?", "a": "O(n²)", "b": "O(n)", "c": "O(n log n)", "d": "O(log n)", "ans": "c"},
        ]
    },
    {
        "code": "INF0203", "title": "Lập trình hướng đối tượng và ứng dụng", "tc": 3,
        "category": "Lập trình", "price": 3 * TC,
        "level": "intermediate",
        "description": "Môn học INF0203 - 3 tín chỉ (60 tiết: 30LT + 30TH). OOP với Python/Java: class, object, 4 tính chất kế thừa, đa hình, đóng gói, trừu tượng.",
        "objectives": "Hiểu và áp dụng 4 tính chất OOP\nXây dựng ứng dụng theo mô hình đối tượng\nSử dụng Design Patterns cơ bản (Singleton, Factory)",
        "requirements": "Đã học INF0433 - Nhập môn lập trình",
        "duration_hours": 60,
        "thumbnail": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&h=400&fit=crop&auto=format",
        "chapters": [
            {"title": "Chương 1: Khái niệm OOP", "lessons": [
                {"title": "Bài 1: OOP là gì? Tại sao cần OOP?", "video_url": "https://www.youtube.com/watch?v=pTB0EiLXUC8", "duration": 18, "preview": True},
                {"title": "Bài 2: Class và Object trong Python", "video_url": "https://www.youtube.com/watch?v=apACNr7DC_s", "duration": 22, "preview": True},
                {"title": "Bài 3: Constructor __init__ và thuộc tính", "video_url": "https://www.youtube.com/watch?v=JeznW_7DlB0", "duration": 20},
            ]},
            {"title": "Chương 2: 4 tính chất OOP", "lessons": [
                {"title": "Bài 4: Encapsulation - Tính đóng gói", "video_url": "https://www.youtube.com/watch?v=y4-6yFMtw2s", "duration": 16},
                {"title": "Bài 5: Inheritance - Kế thừa", "video_url": "https://www.youtube.com/watch?v=RSl87lqOXDE", "duration": 20},
                {"title": "Bài 6: Polymorphism - Đa hình", "video_url": "https://www.youtube.com/watch?v=3ohzBxoFHAY", "duration": 18},
                {"title": "Bài 7: Abstraction - Trừu tượng hóa", "video_url": "https://www.youtube.com/watch?v=o9-WS2SU3s0", "duration": 15},
            ]},
        ],
        "questions": [
            {"content": "Tính chất nào cho phép class con kế thừa từ class cha?", "a": "Encapsulation", "b": "Polymorphism", "c": "Inheritance", "d": "Abstraction", "ans": "c"},
            {"content": "Trong Python, hàm __init__() là hàm gì?", "a": "Destructor", "b": "Constructor", "c": "Static method", "d": "Class method", "ans": "b"},
            {"content": "Encapsulation giúp ẩn chi tiết cài đặt khỏi người dùng bên ngoài.", "type": "true_false", "a": "True", "b": "False", "c": "", "d": "", "ans": "true"},
            {"content": "Từ khóa nào gọi phương thức của class cha trong Python?", "a": "parent()", "b": "super()", "c": "base()", "d": "this()", "ans": "b"},
            {"content": "Polymorphism cho phép điều gì?", "a": "Tạo nhiều object", "b": "Các object khác nhau gọi cùng phương thức nhưng hành vi khác nhau", "c": "Ẩn dữ liệu", "d": "Tái sử dụng code", "ans": "b"},
            {"content": "Thuộc tính private trong Python được đặt tên bắt đầu bằng?", "a": "private_", "b": "__", "c": "#", "d": "@", "ans": "b"},
            {"content": "Method Overriding là gì?", "a": "Định nghĩa nhiều hàm cùng tên", "b": "Class con định nghĩa lại phương thức của class cha", "c": "Gọi hàm từ class khác", "d": "Xóa phương thức", "ans": "b"},
            {"content": "Abstract class có thể tạo object trực tiếp không?", "a": "Có", "b": "Không", "c": "Tùy ngôn ngữ", "d": "Chỉ với Python", "ans": "b"},
        ]
    },
    {
        "code": "INF0083", "title": "Cơ sở dữ liệu", "tc": 3,
        "category": "Cơ sở dữ liệu", "price": 3 * TC,
        "level": "beginner",
        "description": "Môn học INF0083 - 3 tín chỉ (60 tiết: 30LT + 30TH). Mô hình ERD, SQL, thiết kế CSDL quan hệ, chuẩn hóa và tối ưu truy vấn với PostgreSQL.",
        "objectives": "Hiểu mô hình dữ liệu quan hệ và ERD\nViết SQL từ cơ bản đến nâng cao (JOIN, GROUP BY, Subquery)\nChuẩn hóa CSDL đến 3NF",
        "requirements": "Đã học INF0433 - Nhập môn lập trình",
        "duration_hours": 60,
        "thumbnail": "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=800&h=400&fit=crop&auto=format",
        "chapters": [
            {"title": "Chương 1: Tổng quan CSDL", "lessons": [
                {"title": "Bài 1: CSDL là gì? Hệ quản trị CSDL", "video_url": "https://www.youtube.com/watch?v=HXV3zeQKqGY", "duration": 20, "preview": True},
                {"title": "Bài 2: Mô hình quan hệ - Bảng, Hàng, Cột", "video_url": "https://www.youtube.com/watch?v=OqjJjpjDRLc", "duration": 18, "preview": True},
            ]},
            {"title": "Chương 2: Ngôn ngữ SQL", "lessons": [
                {"title": "Bài 3: SELECT cơ bản và WHERE", "video_url": "https://www.youtube.com/watch?v=27axs9dO7AE", "duration": 22},
                {"title": "Bài 4: GROUP BY, HAVING, ORDER BY", "video_url": "https://www.youtube.com/watch?v=p3qvj9hO_Bo", "duration": 25},
                {"title": "Bài 5: JOIN - Kết hợp nhiều bảng", "video_url": "https://www.youtube.com/watch?v=9yeOJ0ZMUYw", "duration": 20},
                {"title": "Bài 6: INSERT, UPDATE, DELETE", "video_url": "https://www.youtube.com/watch?v=-fW2X7fh7Yg", "duration": 15},
            ]},
            {"title": "Chương 3: Thiết kế CSDL", "lessons": [
                {"title": "Bài 7: Mô hình ERD", "video_url": "https://www.youtube.com/watch?v=QpdhBUYk7Kk", "duration": 25},
                {"title": "Bài 8: Chuẩn hóa 1NF, 2NF, 3NF", "video_url": "https://www.youtube.com/watch?v=GFQaEYEc8_8", "duration": 22},
            ]},
        ],
        "questions": [
            {"content": "Câu lệnh SQL nào dùng để lấy dữ liệu từ bảng?", "a": "GET", "b": "SELECT", "c": "FETCH", "d": "PULL", "ans": "b"},
            {"content": "Khóa chính (Primary Key) có thể chứa giá trị NULL.", "type": "true_false", "a": "True", "b": "False", "c": "", "d": "", "ans": "false"},
            {"content": "JOIN nào chỉ lấy bản ghi khớp ở CẢ HAI bảng?", "a": "LEFT JOIN", "b": "RIGHT JOIN", "c": "INNER JOIN", "d": "FULL JOIN", "ans": "c"},
            {"content": "Chuẩn 1NF yêu cầu mỗi ô chứa một giá trị nguyên tố (atomic).", "type": "true_false", "a": "True", "b": "False", "c": "", "d": "", "ans": "true"},
            {"content": "Hàm COUNT() dùng để làm gì?", "a": "Tính tổng", "b": "Tìm max", "c": "Đếm số bản ghi", "d": "Tính trung bình", "ans": "c"},
            {"content": "Khóa ngoại (Foreign Key) dùng để thiết lập quan hệ giữa 2 bảng.", "type": "true_false", "a": "True", "b": "False", "c": "", "d": "", "ans": "true"},
            {"content": "ORDER BY mặc định sắp xếp theo thứ tự nào?", "a": "DESC", "b": "Ngẫu nhiên", "c": "ASC", "d": "Theo thứ tự nhập", "ans": "c"},
            {"content": "Câu lệnh nào xóa tất cả dữ liệu nhưng giữ cấu trúc bảng?", "a": "DROP TABLE", "b": "DELETE FROM (không WHERE)", "c": "TRUNCATE TABLE", "d": "REMOVE ALL", "ans": "c"},
            {"content": "Subquery là gì?", "a": "Bảng tạm thời", "b": "Câu lệnh SELECT lồng trong câu SELECT khác", "c": "Index của bảng", "d": "Khóa ngoại", "ans": "b"},
            {"content": "Lệnh nào tạo bảng mới trong SQL?", "a": "NEW TABLE", "b": "ADD TABLE", "c": "CREATE TABLE", "d": "MAKE TABLE", "ans": "c"},
        ]
    },
    {
        "code": "INF0243", "title": "Lập trình web", "tc": 3,
        "category": "Lập trình Web", "price": 3 * TC,
        "level": "intermediate",
        "description": "Môn học INF0243 - 3 tín chỉ (60 tiết: 30LT + 30TH). HTML5, CSS3, JavaScript, Responsive Design. Xây dựng website thực tế hoàn chỉnh.",
        "objectives": "Xây dựng giao diện web với HTML5 và CSS3\nViết JavaScript xử lý DOM và gọi REST API\nThiết kế Responsive cho mọi thiết bị",
        "requirements": "Đã học INF0433 - Nhập môn lập trình",
        "duration_hours": 60,
        "thumbnail": "https://images.unsplash.com/photo-1547658719-da2b51169166?w=800&h=400&fit=crop&auto=format",
        "chapters": [
            {"title": "Chương 1: HTML5 cơ bản", "lessons": [
                {"title": "Bài 1: HTML là gì? Cấu trúc trang web", "video_url": "https://www.youtube.com/watch?v=qz0aGYrrlhU", "duration": 15, "preview": True},
                {"title": "Bài 2: Các thẻ HTML thông dụng", "video_url": "https://www.youtube.com/watch?v=UB1O30fR-EE", "duration": 22, "preview": True},
                {"title": "Bài 3: Form và Input trong HTML", "video_url": "https://www.youtube.com/watch?v=fNcJuPIZ2WE", "duration": 18},
            ]},
            {"title": "Chương 2: CSS3 và Responsive", "lessons": [
                {"title": "Bài 4: CSS cơ bản - Selector và Properties", "video_url": "https://www.youtube.com/watch?v=1PnVor36_40", "duration": 20},
                {"title": "Bài 5: Flexbox Layout", "video_url": "https://www.youtube.com/watch?v=phWxA89Dy94", "duration": 18},
                {"title": "Bài 6: Responsive - Media Queries", "video_url": "https://www.youtube.com/watch?v=srvUrASNj0s", "duration": 14},
            ]},
            {"title": "Chương 3: JavaScript", "lessons": [
                {"title": "Bài 7: JavaScript cơ bản", "video_url": "https://www.youtube.com/watch?v=hdI2bqOjy3c", "duration": 24},
                {"title": "Bài 8: DOM Manipulation", "video_url": "https://www.youtube.com/watch?v=0ik6X4DJKCc", "duration": 20},
                {"title": "Bài 9: Fetch API - Gọi REST API", "video_url": "https://www.youtube.com/watch?v=cuEtnrL9-H0", "duration": 18},
            ]},
        ],
        "questions": [
            {"content": "Thẻ HTML nào tạo liên kết (hyperlink)?", "a": "<link>", "b": "<a>", "c": "<href>", "d": "<url>", "ans": "b"},
            {"content": "CSS selector nào chọn phần tử có id='header'?", "a": ".header", "b": "header", "c": "#header", "d": "*header", "ans": "c"},
            {"content": "Cách khai báo biến không thay đổi trong JavaScript?", "a": "var", "b": "let", "c": "const", "d": "static", "ans": "c"},
            {"content": "HTML là ngôn ngữ lập trình.", "type": "true_false", "a": "True", "b": "False", "c": "", "d": "", "ans": "false"},
            {"content": "Phương thức HTTP nào lấy dữ liệu từ server?", "a": "POST", "b": "PUT", "c": "DELETE", "d": "GET", "ans": "d"},
            {"content": "Flexbox tạo layout theo mấy chiều?", "a": "1 chiều", "b": "2 chiều", "c": "3 chiều", "d": "Không chiều", "ans": "a"},
            {"content": "CSS Grid khác Flexbox ở điểm nào?", "a": "Grid là 2 chiều (hàng và cột)", "b": "Grid chỉ dành cho mobile", "c": "Grid không hỗ trợ responsive", "d": "Không khác gì", "ans": "a"},
            {"content": "Responsive Design giúp website hiển thị tốt trên mọi kích thước màn hình.", "type": "true_false", "a": "True", "b": "False", "c": "", "d": "", "ans": "true"},
            {"content": "Thẻ nào hiển thị tiêu đề quan trọng nhất?", "a": "<h6>", "b": "<title>", "c": "<h1>", "d": "<header>", "ans": "c"},
            {"content": "JSON là gì?", "a": "Ngôn ngữ lập trình", "b": "Định dạng trao đổi dữ liệu dựa trên JavaScript", "c": "Framework CSS", "d": "Database", "ans": "b"},
        ]
    },
    {
        "code": "INF0883", "title": "Mạng máy tính và Hệ điều hành", "tc": 3,
        "category": "Hệ thống", "price": 3 * TC,
        "level": "intermediate",
        "description": "Môn học INF0883 - 3 tín chỉ (60 tiết: 30LT + 30TH). Mô hình OSI/TCP-IP, giao thức mạng, địa chỉ IP và Linux command line.",
        "objectives": "Hiểu mô hình OSI 7 tầng và TCP/IP\nCấu hình mạng và địa chỉ IP\nThành thạo Linux command line cơ bản",
        "requirements": "Không yêu cầu kinh nghiệm trước",
        "duration_hours": 60,
        "thumbnail": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&h=400&fit=crop&auto=format",
        "chapters": [
            {"title": "Chương 1: Mạng máy tính cơ bản", "lessons": [
                {"title": "Bài 1: Mạng máy tính và lịch sử Internet", "video_url": "https://www.youtube.com/watch?v=3QhU9jd03a0", "duration": 20, "preview": True},
                {"title": "Bài 2: Mô hình OSI 7 tầng", "video_url": "https://www.youtube.com/watch?v=vv4y_uOneC0", "duration": 22, "preview": True},
                {"title": "Bài 3: TCP/IP và địa chỉ IP", "video_url": "https://www.youtube.com/watch?v=L3ZzkOTDins", "duration": 18},
            ]},
            {"title": "Chương 2: Hệ điều hành Linux", "lessons": [
                {"title": "Bài 4: Linux là gì? Cài đặt Ubuntu", "video_url": "https://www.youtube.com/watch?v=rrB13utjYV4", "duration": 16},
                {"title": "Bài 5: Linux Command Line cơ bản", "video_url": "https://www.youtube.com/watch?v=s3ii48qYBxA", "duration": 25},
                {"title": "Bài 6: Quản lý file và permission", "video_url": "https://www.youtube.com/watch?v=zaJZMFB7MfA", "duration": 20},
            ]},
        ],
        "questions": [
            {"content": "Mô hình OSI có bao nhiêu tầng?", "a": "4", "b": "5", "c": "7", "d": "8", "ans": "c"},
            {"content": "HTTP hoạt động ở tầng nào của OSI?", "a": "Tầng 3 Network", "b": "Tầng 4 Transport", "c": "Tầng 7 Application", "d": "Tầng 2 Data Link", "ans": "c"},
            {"content": "192.168.1.1 là loại địa chỉ IP gì?", "a": "Public IP", "b": "Private IP", "c": "Multicast IP", "d": "Broadcast IP", "ans": "b"},
            {"content": "TCP đảm bảo truyền dữ liệu tin cậy hơn UDP.", "type": "true_false", "a": "True", "b": "False", "c": "", "d": "", "ans": "true"},
            {"content": "Lệnh Linux nào liệt kê file trong thư mục?", "a": "dir", "b": "ls", "c": "list", "d": "show", "ans": "b"},
            {"content": "DNS có chức năng gì?", "a": "Mã hóa dữ liệu", "b": "Phân giải tên miền thành địa chỉ IP", "c": "Tăng tốc mạng", "d": "Firewall", "ans": "b"},
            {"content": "Port mặc định của HTTPS là?", "a": "80", "b": "21", "c": "443", "d": "8080", "ans": "c"},
            {"content": "Lệnh chmod 755 cho phép chủ sở hữu đọc+ghi+thực thi, group và others đọc+thực thi.", "type": "true_false", "a": "True", "b": "False", "c": "", "d": "", "ans": "true"},
        ]
    },
    {
        "code": "INF0103", "title": "Nhập môn Trí tuệ nhân tạo", "tc": 3,
        "category": "Trí tuệ nhân tạo", "price": 3 * TC,
        "level": "intermediate",
        "description": "Môn học INF0103 - 3 tín chỉ (60 tiết: 30LT + 30TH). Machine Learning, Neural Network, Deep Learning và ứng dụng AI thực tế với Python.",
        "objectives": "Hiểu các thuật toán Machine Learning cơ bản\nXây dựng Neural Network với Python/TensorFlow\nÁp dụng AI vào các bài toán thực tế",
        "requirements": "Đã học INF0433 và Toán đại số tuyến tính",
        "duration_hours": 60,
        "thumbnail": "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=800&h=400&fit=crop&auto=format",
        "chapters": [
            {"title": "Chương 1: Giới thiệu AI và ML", "lessons": [
                {"title": "Bài 1: AI là gì? Lịch sử phát triển", "video_url": "https://www.youtube.com/watch?v=JMUxmLyrhSk", "duration": 25, "preview": True},
                {"title": "Bài 2: AI vs ML vs Deep Learning", "video_url": "https://www.youtube.com/watch?v=aircAruvnKk", "duration": 20, "preview": True},
            ]},
            {"title": "Chương 2: Machine Learning cơ bản", "lessons": [
                {"title": "Bài 3: Linear Regression - Hồi quy tuyến tính", "video_url": "https://www.youtube.com/watch?v=NUXdtN1W1FE", "duration": 22},
                {"title": "Bài 4: Logistic Regression - Phân loại", "video_url": "https://www.youtube.com/watch?v=yIYKR4sgzI8", "duration": 20},
                {"title": "Bài 5: Decision Tree và Random Forest", "video_url": "https://www.youtube.com/watch?v=7VeUPuFGJHk", "duration": 18},
            ]},
            {"title": "Chương 3: Neural Network", "lessons": [
                {"title": "Bài 6: Neural Network hoạt động thế nào?", "video_url": "https://www.youtube.com/watch?v=aircAruvnKk", "duration": 19},
                {"title": "Bài 7: Xây dựng NN với TensorFlow", "video_url": "https://www.youtube.com/watch?v=Wo5dMEP_BbI", "duration": 25},
            ]},
        ],
        "questions": [
            {"content": "Machine Learning là gì?", "a": "Máy học từ kinh nghiệm không cần lập trình tường minh", "b": "Robot có thể đi lại", "c": "Phần mềm diệt virus", "d": "Ngôn ngữ lập trình mới", "ans": "a"},
            {"content": "Thuật toán nào phù hợp dự đoán giá nhà (số liên tục)?", "a": "Logistic Regression", "b": "Linear Regression", "c": "K-Means", "d": "Naive Bayes", "ans": "b"},
            {"content": "Supervised Learning học từ dữ liệu có nhãn (label).", "type": "true_false", "a": "True", "b": "False", "c": "", "d": "", "ans": "true"},
            {"content": "Overfitting xảy ra khi nào?", "a": "Model học quá tốt training data nhưng kém trên data mới", "b": "Model không học được", "c": "Dữ liệu quá ít", "d": "Model quá đơn giản", "ans": "a"},
            {"content": "ChatGPT là ví dụ của dạng AI nào?", "a": "Computer Vision", "b": "Reinforcement Learning", "c": "NLP - Xử lý ngôn ngữ tự nhiên", "d": "Robotics", "ans": "c"},
            {"content": "Hàm activation ReLU trả về gì khi đầu vào âm?", "a": "Giá trị âm đó", "b": "0", "c": "1", "d": "-1", "ans": "b"},
            {"content": "Deep Learning là một nhánh của Machine Learning.", "type": "true_false", "a": "True", "b": "False", "c": "", "d": "", "ans": "true"},
            {"content": "k-means là thuật toán học gì?", "a": "Supervised Learning", "b": "Reinforcement Learning", "c": "Unsupervised Learning", "d": "Semi-supervised", "ans": "c"},
            {"content": "Confusion Matrix dùng để đánh giá điều gì?", "a": "Tốc độ model", "b": "Độ chính xác model phân loại", "c": "Kích thước dataset", "d": "Số lớp ẩn", "ans": "b"},
            {"content": "Epoch trong ML nghĩa là gì?", "a": "Số lần model xem qua toàn bộ training data", "b": "Kích thước batch", "c": "Learning rate", "d": "Số lớp ẩn", "ans": "a"},
        ]
    },
    {
        "code": "INF1003", "title": "Điện toán đám mây", "tc": 3,
        "category": "Hệ thống", "price": 3 * TC,
        "level": "advanced",
        "description": "Môn học INF1003 - 3 tín chỉ (60 tiết: 30LT + 30TH). Cloud Computing: AWS, Azure, GCP. Docker, Kubernetes, CI/CD và DevOps.",
        "objectives": "Hiểu các mô hình IaaS, PaaS, SaaS\nTriển khai ứng dụng lên Cloud (AWS/Render/Vercel)\nSử dụng Docker và CI/CD pipeline",
        "requirements": "Đã học INF0883 - Mạng máy tính",
        "duration_hours": 60,
        "thumbnail": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&h=400&fit=crop&auto=format",
        "chapters": [
            {"title": "Chương 1: Cloud Computing cơ bản", "lessons": [
                {"title": "Bài 1: Cloud Computing là gì?", "video_url": "https://www.youtube.com/watch?v=M988_fsOSWo", "duration": 20, "preview": True},
                {"title": "Bài 2: IaaS vs PaaS vs SaaS", "video_url": "https://www.youtube.com/watch?v=9CVBohl6w0Q", "duration": 16, "preview": True},
            ]},
            {"title": "Chương 2: Docker và Container", "lessons": [
                {"title": "Bài 3: Docker là gì? Container vs VM", "video_url": "https://www.youtube.com/watch?v=Gjnup-PuquQ", "duration": 22},
                {"title": "Bài 4: Dockerfile và Docker Compose", "video_url": "https://www.youtube.com/watch?v=DM65_JyGxCo", "duration": 25},
                {"title": "Bài 5: Deploy app lên Render/Railway", "video_url": "https://www.youtube.com/watch?v=M988_fsOSWo", "duration": 18},
            ]},
        ],
        "questions": [
            {"content": "IaaS trong Cloud Computing là gì?", "a": "Infrastructure as a Service - thuê cơ sở hạ tầng", "b": "Internet as a Service", "c": "Intelligence as a Service", "d": "Integration as a Service", "ans": "a"},
            {"content": "Container khác Virtual Machine ở điểm nào?", "a": "Container nặng hơn VM", "b": "Container chia sẻ OS kernel, nhẹ và khởi động nhanh hơn", "c": "Container chậm hơn VM", "d": "Không có sự khác biệt", "ans": "b"},
            {"content": "Dockerfile là file chứa hướng dẫn để build Docker image.", "type": "true_false", "a": "True", "b": "False", "c": "", "d": "", "ans": "true"},
            {"content": "CI/CD viết tắt của gì?", "a": "Cloud Integration / Cloud Deployment", "b": "Continuous Integration / Continuous Deployment", "c": "Code Inspection / Code Delivery", "d": "Computer Integration / Computer Deployment", "ans": "b"},
            {"content": "Kubernetes dùng để làm gì?", "a": "Viết code nhanh hơn", "b": "Quản lý và điều phối nhiều container", "c": "Tạo database", "d": "Thiết kế giao diện", "ans": "b"},
            {"content": "Auto-scaling của Cloud cho phép tự động tăng/giảm tài nguyên theo tải.", "type": "true_false", "a": "True", "b": "False", "c": "", "d": "", "ans": "true"},
            {"content": "Lệnh nào khởi động Docker Compose?", "a": "docker start", "b": "docker run", "c": "docker-compose up", "d": "docker init", "ans": "c"},
            {"content": "Render.com sử dụng hạ tầng Cloud nào bên dưới?", "a": "AWS", "b": "Azure", "c": "GCP", "d": "IBM Cloud", "ans": "a"},
        ]
    },
    {
        "code": "INF0893", "title": "Mật mã và An toàn thông tin", "tc": 3,
        "category": "An toàn thông tin", "price": 3 * TC,
        "level": "intermediate",
        "description": "Môn học INF0893 - 3 tín chỉ (60 tiết: 30LT + 30TH). Mã hóa đối xứng/bất đối xứng, hash, PKI, JWT, bảo mật ứng dụng web (SQL Injection, XSS).",
        "objectives": "Hiểu các thuật toán mã hóa AES, RSA\nÁp dụng bảo mật JWT trong ứng dụng web\nNhận biết và phòng chống SQL Injection, XSS",
        "requirements": "Đã học INF0883 - Mạng máy tính",
        "duration_hours": 60,
        "thumbnail": "https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=800&h=400&fit=crop&auto=format",
        "chapters": [
            {"title": "Chương 1: Mật mã học cơ bản", "lessons": [
                {"title": "Bài 1: Mật mã là gì? Lịch sử mã hóa", "video_url": "https://www.youtube.com/watch?v=AQDCe585Lnc", "duration": 18, "preview": True},
                {"title": "Bài 2: Mã hóa đối xứng AES", "video_url": "https://www.youtube.com/watch?v=O4xNJsjtN6E", "duration": 20, "preview": True},
                {"title": "Bài 3: Mã hóa bất đối xứng RSA", "video_url": "https://www.youtube.com/watch?v=wXB-V_Keiu8", "duration": 22},
            ]},
            {"title": "Chương 2: Bảo mật ứng dụng", "lessons": [
                {"title": "Bài 4: Hash Function MD5 SHA256", "video_url": "https://www.youtube.com/watch?v=b4b8ktEV4Bg", "duration": 16},
                {"title": "Bài 5: SQL Injection và phòng chống", "video_url": "https://www.youtube.com/watch?v=ciNHn38EyRc", "duration": 20},
                {"title": "Bài 6: HTTPS và SSL/TLS", "video_url": "https://www.youtube.com/watch?v=67kItGjvgCE", "duration": 18},
            ]},
        ],
        "questions": [
            {"content": "Mã hóa đối xứng nghĩa là dùng cùng 1 khóa để mã hóa và giải mã.", "type": "true_false", "a": "True", "b": "False", "c": "", "d": "", "ans": "true"},
            {"content": "RSA là thuật toán mã hóa gì?", "a": "Đối xứng", "b": "Bất đối xứng (khóa công khai)", "c": "Hash", "d": "Stream cipher", "ans": "b"},
            {"content": "Hash function có tính chất không thể đảo ngược (one-way).", "type": "true_false", "a": "True", "b": "False", "c": "", "d": "", "ans": "true"},
            {"content": "SQL Injection tấn công vào đâu?", "a": "Mạng máy tính", "b": "Hệ điều hành", "c": "Input của ứng dụng web để thao túng SQL", "d": "File hệ thống", "ans": "c"},
            {"content": "HTTPS khác HTTP vì mã hóa dữ liệu truyền bằng SSL/TLS.", "type": "true_false", "a": "True", "b": "False", "c": "", "d": "", "ans": "true"},
            {"content": "AES dùng khóa có độ dài bao nhiêu bit?", "a": "64 bit", "b": "128, 192 hoặc 256 bit", "c": "512 bit", "d": "1024 bit", "ans": "b"},
            {"content": "JWT Token sử dụng thuật toán gì để ký?", "a": "MD5", "b": "Base64", "c": "HMAC-SHA256 hoặc RSA", "d": "AES", "ans": "c"},
            {"content": "XSS là loại tấn công chèn script độc hại vào trang web.", "type": "true_false", "a": "True", "b": "False", "c": "", "d": "", "ans": "true"},
        ]
    },
]


class Command(BaseCommand):
    help = 'Seed môn học CNTT Bình Dương - giá theo tín chỉ (1TC = 750.000đ)'

    def handle(self, *args, **kwargs):
        self.stdout.write('📚 Bắt đầu seed môn học CNTT Bình Dương...')

        try:
            instructor = User.objects.get(email='gv1@elearning.com')
        except User.DoesNotExist:
            self.stdout.write('⚠️ Chưa có GV1, chạy seed_data trước!')
            return

        # Tạo categories
        cat_icons = {
            'Lập trình': '💻', 'Cơ sở dữ liệu': '🗄️',
            'Lập trình Web': '🌐', 'Trí tuệ nhân tạo': '🤖',
            'Hệ thống': '⚙️', 'An toàn thông tin': '🔒',
        }
        cat_map = {}
        for data in COURSES_DATA:
            name = data['category']
            if name not in cat_map:
                cat, _ = Category.objects.get_or_create(
                    name=name,
                    defaults={
                        'slug': slugify(name) + '-' + str(uuid.uuid4())[:4],
                        'icon': cat_icons.get(name, '📚'),
                        'description': f'Danh mục {name}',
                    }
                )
                cat_map[name] = cat

        # Tạo courses
        created_count = 0
        for data in COURSES_DATA:
            course, created = Course.objects.get_or_create(
                title=data['title'],
                defaults={
                    'slug': slugify(data['title']) + '-' + str(uuid.uuid4())[:6],
                    'instructor': instructor,
                    'category': cat_map[data['category']],
                    'description': data['description'],
                    'price': data['price'],
                    'level': data['level'],
                    'status': 'published',
                    'duration_hours': data['duration_hours'],
                    'objectives': data.get('objectives', ''),
                    'requirements': data.get('requirements', ''),
                    'thumbnail': data.get('thumbnail', ''),
                }
            )

            if not created:
                # Cập nhật thumbnail và price nếu đã có
                Course.objects.filter(id=course.id).update(
                    thumbnail=data.get('thumbnail', ''),
                    price=data['price'],
                )
                self.stdout.write(f'  🔄 Cập nhật: {data["code"]} - {data["title"]}')
                continue

            # Tạo chapters và lessons
            for ci, ch in enumerate(data['chapters']):
                chapter = Chapter.objects.create(
                    course=course, title=ch['title'], order=ci + 1
                )
                for li, lesson in enumerate(ch['lessons']):
                    Lesson.objects.create(
                        chapter=chapter,
                        title=lesson['title'],
                        content_type='video',
                        video_url=lesson['video_url'],
                        duration=lesson['duration'],
                        order=li + 1,
                        is_preview=lesson.get('preview', False),
                        content=f"Nội dung: {lesson['title']}",
                    )

            # Tạo exam
            exam = Exam.objects.create(
                course=course,
                title=f'Kiểm tra - {data["title"]}',
                description=f'Kiểm tra kiến thức môn {data["code"]} - {data["title"]}',
                duration_minutes=30,
                total_questions=min(10, len(data['questions'])),
                pass_score=60,
                is_random=True,
                is_active=True,
            )
            for qi, q in enumerate(data['questions']):
                Question.objects.create(
                    exam=exam,
                    content=q['content'],
                    question_type=q.get('type', 'multiple_choice'),
                    option_a=q.get('a', ''),
                    option_b=q.get('b', ''),
                    option_c=q.get('c', ''),
                    option_d=q.get('d', ''),
                    correct_answer=q['ans'],
                    points=1,
                    order=qi + 1,
                )

            tc = data['tc']
            price_str = 'Miễn phí' if data['price'] == 0 else f"{data['price']:,}đ"
            self.stdout.write(f'  ✅ {data["code"]}: {data["title"]} | {tc}TC | {price_str}')
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f'''
╔══════════════════════════════════════════════════╗
║  🎉 Seed {created_count} môn học CNTT Bình Dương xong!     ║
║  💰 Học phí: 1 tín chỉ = 750.000đ               ║
║  📚 3 tín chỉ = 2.250.000đ/môn                  ║
╚══════════════════════════════════════════════════╝
        '''))
