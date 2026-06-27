from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.users.models import User
from apps.courses.models import Category, Course, Chapter
from apps.lessons.models import Lesson
from apps.exams.models import Exam, Question
from apps.enrollments.models import Enrollment
from apps.reviews.models import Review
import uuid


class Command(BaseCommand):
    help = 'Seed database với dữ liệu mẫu thật - Đại học Bình Dương'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱 Bắt đầu seed dữ liệu thật...')

        # 1. Users
        admin = self._user('admin@elearning.com', 'Admin Hệ thống', 'admin', 'Admin@123')
        gv1 = self._user('gv1@elearning.com', 'TS. Nguyễn Văn An', 'instructor', 'Gv@123456')
        gv2 = self._user('gv2@elearning.com', 'ThS. Trần Thị Bích', 'instructor', 'Gv@123456')
        gv3 = self._user('gv3@elearning.com', 'TS. Lê Minh Tuấn', 'instructor', 'Gv@123456')
        sv1 = self._user('sv1@elearning.com', 'Nguyễn Văn Cường', 'student', 'Sv@123456')
        sv2 = self._user('sv2@elearning.com', 'Trần Thị Dung', 'student', 'Sv@123456')
        sv3 = self._user('sv3@elearning.com', 'Lê Văn Em', 'student', 'Sv@123456')
        self.stdout.write('✅ Users done')

        # 2. Categories - Các khoa của ĐH Bình Dương
        cats = {
            'cntt': self._cat('Công nghệ thông tin', 'cong-nghe-thong-tin', '💻'),
            'kinh-te': self._cat('Kinh tế - Quản trị', 'kinh-te-quan-tri', '📊'),
            'ngon-ngu': self._cat('Ngôn ngữ Anh', 'ngon-ngu-anh', '🌍'),
            'luat': self._cat('Luật', 'luat', '⚖️'),
            'dien': self._cat('Điện - Điện tử', 'dien-dien-tu', '⚡'),
            'xd': self._cat('Xây dựng - Kiến trúc', 'xay-dung-kien-truc', '🏗️'),
            'duoc': self._cat('Dược học', 'duoc-hoc', '💊'),
            'co-so': self._cat('Đại cương', 'dai-cuong', '📚'),
        }
        self.stdout.write('✅ Categories done')

        # 3. Courses với nội dung thật
        courses_data = [
            # CNTT
            {
                'title': 'Lập trình Python cơ bản đến nâng cao',
                'cat': 'cntt', 'instructor': gv1, 'price': 299000, 'level': 'beginner',
                'desc': 'Khóa học Python toàn diện từ cơ bản đến nâng cao. Học cú pháp, OOP, xử lý file, thư viện NumPy, Pandas và ứng dụng thực tế.',
                'obj': 'Nắm vững cú pháp Python\nViết chương trình OOP\nXử lý dữ liệu với Pandas\nXây dựng ứng dụng thực tế',
                'req': 'Có máy tính cài Python\nKiến thức toán cơ bản',
                'hours': 30,
                'chapters': [
                    ('Chương 1: Giới thiệu Python & Cài đặt', [
                        ('Python là gì? Tại sao chọn Python?', 'https://www.youtube.com/embed/rfscVS0vtbw', 15),
                        ('Cài đặt Python & VS Code', 'https://www.youtube.com/embed/YYXdXT2l-Gg', 12),
                        ('Chạy chương trình Python đầu tiên', 'https://www.youtube.com/embed/kqtD5dpn9C8', 10),
                    ]),
                    ('Chương 2: Biến, Kiểu dữ liệu & Toán tử', [
                        ('Biến và kiểu dữ liệu trong Python', 'https://www.youtube.com/embed/khKv-8q7YmY', 20),
                        ('Chuỗi (String) và các phương thức', 'https://www.youtube.com/embed/k9TUPpGqYTo', 18),
                        ('List, Tuple, Dictionary, Set', 'https://www.youtube.com/embed/W8KRzm-HUcc', 22),
                    ]),
                    ('Chương 3: Cấu trúc điều khiển', [
                        ('Câu lệnh if-elif-else', 'https://www.youtube.com/embed/f4KOjWS_KZs', 15),
                        ('Vòng lặp for và while', 'https://www.youtube.com/embed/OnDr4J2UXSA', 20),
                        ('Hàm (Function) trong Python', 'https://www.youtube.com/embed/9Os0o3wzS_I', 25),
                    ]),
                ],
                'exam': {
                    'title': 'Kiểm tra cuối khóa - Python cơ bản',
                    'duration': 30, 'pass_score': 60,
                    'questions': [
                        ('Python là ngôn ngữ lập trình thuộc loại nào?', 'a', 'Thông dịch (Interpreted)', 'Biên dịch (Compiled)', 'Hợp ngữ (Assembly)', 'Máy (Machine)'),
                        ('Kết quả của lệnh print(type(3.14)) là gì?', 'b', 'int', 'float', 'str', 'double'),
                        ('Cú pháp định nghĩa hàm trong Python?', 'a', 'def ten_ham():', 'function ten_ham():', 'void ten_ham():', 'func ten_ham():'),
                        ('List trong Python có đặc điểm gì?', 'c', 'Không thay đổi được', 'Chỉ chứa số', 'Có thể thay đổi', 'Chỉ chứa chuỗi'),
                        ('Vòng lặp nào dùng khi biết trước số lần lặp?', 'a', 'for', 'while', 'do-while', 'loop'),
                        ('Kết quả của 10 // 3 trong Python?', 'b', '3.33', '3', '4', '1'),
                        ('Từ khóa nào dùng để kế thừa class trong Python?', 'c', 'extends', 'implements', 'Viết tên lớp cha trong ngoặc', 'inherit'),
                        ('Phương thức nào thêm phần tử vào cuối List?', 'a', 'append()', 'add()', 'push()', 'insert()'),
                        ('Dictionary trong Python lưu dữ liệu theo dạng gì?', 'b', 'Danh sách', 'Cặp key-value', 'Tập hợp', 'Mảng'),
                        ('Câu lệnh nào dùng để bắt lỗi trong Python?', 'c', 'catch-throw', 'error-handle', 'try-except', 'if-error'),
                    ]
                }
            },
            {
                'title': 'Lập trình Web với Django Framework',
                'cat': 'cntt', 'instructor': gv1, 'price': 399000, 'level': 'intermediate',
                'desc': 'Xây dựng ứng dụng web hoàn chỉnh với Django. Học models, views, templates, REST API, authentication và deploy lên Cloud.',
                'obj': 'Xây dựng web với Django\nThiết kế database Models\nTạo REST API với DRF\nDeploy ứng dụng lên server',
                'req': 'Biết Python cơ bản\nHiểu HTML/CSS cơ bản',
                'hours': 40,
                'chapters': [
                    ('Chương 1: Giới thiệu Django', [
                        ('Django là gì? MTV Architecture', 'https://www.youtube.com/embed/F5mRW0jo-U4', 18),
                        ('Tạo project Django đầu tiên', 'https://www.youtube.com/embed/rHux0gMZ3Eg', 20),
                        ('URL routing và Views cơ bản', 'https://www.youtube.com/embed/71ruqrZv8fA', 22),
                    ]),
                    ('Chương 2: Models & Database', [
                        ('Django Models và ORM', 'https://www.youtube.com/embed/OcS_DZNHpnI', 25),
                        ('Migrations và Admin site', 'https://www.youtube.com/embed/UmljXZIypDc', 20),
                        ('QuerySet API - Truy vấn dữ liệu', 'https://www.youtube.com/embed/WimXjp0ryOo', 30),
                    ]),
                    ('Chương 3: REST API với DRF', [
                        ('Giới thiệu Django REST Framework', 'https://www.youtube.com/embed/c708Nf0cHrs', 25),
                        ('Serializers và ViewSets', 'https://www.youtube.com/embed/B38aDwUpcFc', 30),
                        ('Authentication JWT trong DRF', 'https://www.youtube.com/embed/PUzgZrS_piQ', 28),
                    ]),
                ],
                'exam': {
                    'title': 'Kiểm tra Django Framework',
                    'duration': 30, 'pass_score': 60,
                    'questions': [
                        ('Django theo mô hình kiến trúc nào?', 'b', 'MVC', 'MVT (Model-View-Template)', 'MVVM', 'MVP'),
                        ('File nào chứa cấu hình chính của Django project?', 'a', 'settings.py', 'urls.py', 'models.py', 'views.py'),
                        ('Lệnh nào tạo migration trong Django?', 'b', 'python manage.py migrate', 'python manage.py makemigrations', 'python manage.py createdb', 'python manage.py syncdb'),
                        ('ORM trong Django viết câu truy vấn lấy tất cả object?', 'a', 'Model.objects.all()', 'Model.getAll()', 'Model.find()', 'Model.select()'),
                        ('Django REST Framework dùng để làm gì?', 'c', 'Tạo template HTML', 'Quản lý database', 'Xây dựng REST API', 'Deploy ứng dụng'),
                        ('Serializer trong DRF có chức năng gì?', 'b', 'Render HTML', 'Chuyển đổi data sang JSON', 'Xử lý URL', 'Kết nối database'),
                        ('Middleware trong Django xử lý ở đâu?', 'a', 'Giữa request và response', 'Trong database', 'Trong template', 'Trong model'),
                        ('Lệnh chạy server Django?', 'b', 'python manage.py start', 'python manage.py runserver', 'python manage.py serve', 'django run'),
                        ('ForeignKey trong Django tạo quan hệ nào?', 'b', 'Nhiều-Nhiều', 'Một-Nhiều', 'Một-Một', 'Tự tham chiếu'),
                        ('WSGI là gì trong Django deployment?', 'a', 'Web Server Gateway Interface', 'Web Service General Interface', 'Web Security Gateway', 'None'),
                    ]
                }
            },
            {
                'title': 'Cơ sở dữ liệu - SQL & PostgreSQL',
                'cat': 'cntt', 'instructor': gv2, 'price': 249000, 'level': 'beginner',
                'desc': 'Học SQL từ cơ bản: SELECT, INSERT, UPDATE, DELETE. Thiết kế database, chuẩn hóa, index, stored procedure với PostgreSQL.',
                'obj': 'Thành thạo câu lệnh SQL\nThiết kế CSDL chuẩn hóa\nVẽ ERD và Data Dictionary\nDùng PostgreSQL thành thạo',
                'req': 'Không yêu cầu kinh nghiệm\nCó máy tính cài PostgreSQL',
                'hours': 25,
                'chapters': [
                    ('Chương 1: Giới thiệu CSDL & SQL', [
                        ('CSDL là gì? Các loại CSDL', 'https://www.youtube.com/embed/FR4QIeZaPeM', 15),
                        ('Cài đặt PostgreSQL & pgAdmin', 'https://www.youtube.com/embed/-LwI4HMR_Eg', 12),
                        ('Câu lệnh DDL: CREATE, ALTER, DROP', 'https://www.youtube.com/embed/nWeW3sCmD2k', 20),
                    ]),
                    ('Chương 2: Truy vấn dữ liệu', [
                        ('SELECT - Lấy dữ liệu cơ bản', 'https://www.youtube.com/embed/HXV3zeQKqGY', 25),
                        ('WHERE, ORDER BY, GROUP BY, HAVING', 'https://www.youtube.com/embed/3UYTe-KKl7Q', 28),
                        ('JOIN - Kết hợp nhiều bảng', 'https://www.youtube.com/embed/9yeOJ0ZMUYw', 30),
                    ]),
                    ('Chương 3: Thiết kế CSDL', [
                        ('ERD và thiết kế quan hệ', 'https://www.youtube.com/embed/QpdhBUYk7Kk', 22),
                        ('Chuẩn hóa 1NF, 2NF, 3NF', 'https://www.youtube.com/embed/GFQaEYEc8_8', 25),
                        ('Index và tối ưu truy vấn', 'https://www.youtube.com/embed/fsG1XaZEa78', 20),
                    ]),
                ],
                'exam': {
                    'title': 'Kiểm tra Cơ sở dữ liệu SQL',
                    'duration': 25, 'pass_score': 60,
                    'questions': [
                        ('Lệnh SQL nào dùng để lấy dữ liệu?', 'a', 'SELECT', 'GET', 'FETCH', 'READ'),
                        ('PRIMARY KEY có đặc điểm gì?', 'b', 'Có thể NULL', 'Duy nhất và không NULL', 'Có thể trùng', 'Tùy chọn'),
                        ('INNER JOIN trả về kết quả nào?', 'c', 'Tất cả bản ghi bảng trái', 'Tất cả bản ghi bảng phải', 'Chỉ bản ghi khớp cả 2 bảng', 'Tất cả bản ghi'),
                        ('GROUP BY dùng để làm gì?', 'b', 'Sắp xếp dữ liệu', 'Nhóm dữ liệu để tổng hợp', 'Lọc dữ liệu', 'Kết hợp bảng'),
                        ('Hàm nào đếm số bản ghi?', 'a', 'COUNT()', 'SUM()', 'TOTAL()', 'NUMBER()'),
                        ('FOREIGN KEY dùng để làm gì?', 'c', 'Tăng tốc truy vấn', 'Mã hóa dữ liệu', 'Tạo quan hệ giữa 2 bảng', 'Backup dữ liệu'),
                        ('Chuẩn hóa 3NF yêu cầu gì?', 'b', '1NF', 'Thỏa 2NF và không có phụ thuộc bắc cầu', 'Không có phụ thuộc hàm', 'Chỉ có 1 bảng'),
                        ('Lệnh xóa toàn bộ dữ liệu trong bảng nhưng giữ cấu trúc?', 'b', 'DROP TABLE', 'TRUNCATE TABLE', 'DELETE TABLE', 'REMOVE TABLE'),
                        ('NULL trong SQL có nghĩa là gì?', 'a', 'Không có giá trị', 'Bằng 0', 'Chuỗi rỗng', 'False'),
                        ('HAVING khác WHERE ở điểm nào?', 'c', 'HAVING nhanh hơn', 'WHERE dùng với GROUP BY', 'HAVING dùng với GROUP BY', 'Không khác nhau'),
                    ]
                }
            },
            {
                'title': 'Cấu trúc dữ liệu và Giải thuật',
                'cat': 'cntt', 'instructor': gv3, 'price': 349000, 'level': 'intermediate',
                'desc': 'Học các cấu trúc dữ liệu quan trọng: Array, Linked List, Stack, Queue, Tree, Graph và các giải thuật sắp xếp, tìm kiếm.',
                'obj': 'Hiểu và cài đặt CTDL cơ bản\nPhân tích độ phức tạp thuật toán\nCài đặt giải thuật sắp xếp\nGiải bài toán thực tế',
                'req': 'Biết 1 ngôn ngữ lập trình\nHiểu vòng lặp và hàm',
                'hours': 35,
                'chapters': [
                    ('Chương 1: Array & Linked List', [
                        ('Mảng (Array) và ứng dụng', 'https://www.youtube.com/embed/QJNwK2uJyGs', 20),
                        ('Danh sách liên kết (Linked List)', 'https://www.youtube.com/embed/njTh_OwMljA', 25),
                        ('Stack và Queue', 'https://www.youtube.com/embed/wjI1WNcIntg', 22),
                    ]),
                    ('Chương 2: Giải thuật sắp xếp', [
                        ('Bubble Sort, Selection Sort', 'https://www.youtube.com/embed/xWBP4knPcgc', 18),
                        ('Merge Sort và Quick Sort', 'https://www.youtube.com/embed/4VqmGXwpLqc', 25),
                        ('Phân tích độ phức tạp Big-O', 'https://www.youtube.com/embed/__vX2sjlpXU', 20),
                    ]),
                    ('Chương 3: Cây và Đồ thị', [
                        ('Binary Tree và BST', 'https://www.youtube.com/embed/oSWTXtMglKE', 28),
                        ('DFS và BFS trên đồ thị', 'https://www.youtube.com/embed/pcKY4hjDrxk', 30),
                        ('Bài tập tổng hợp', 'https://www.youtube.com/embed/fAAZixBzIAI', 35),
                    ]),
                ],
                'exam': {
                    'title': 'Kiểm tra CTDL & Giải thuật',
                    'duration': 30, 'pass_score': 60,
                    'questions': [
                        ('Stack hoạt động theo nguyên tắc nào?', 'a', 'LIFO - Last In First Out', 'FIFO - First In First Out', 'Random', 'Priority'),
                        ('Queue hoạt động theo nguyên tắc nào?', 'b', 'LIFO', 'FIFO - First In First Out', 'Random', 'Priority'),
                        ('Độ phức tạp của Bubble Sort trong trường hợp xấu nhất?', 'c', 'O(n)', 'O(n log n)', 'O(n²)', 'O(log n)'),
                        ('Binary Search yêu cầu mảng phải như thế nào?', 'a', 'Đã được sắp xếp', 'Không trùng lặp', 'Số nguyên dương', 'Có ít nhất 10 phần tử'),
                        ('Linked List khác Array ở điểm nào?', 'b', 'Lưu liên tục trong bộ nhớ', 'Các node không liên tục, kết nối bằng con trỏ', 'Chỉ chứa số', 'Có kích thước cố định'),
                        ('DFS là viết tắt của gì?', 'a', 'Depth First Search', 'Data First Search', 'Direct File System', 'Dynamic Function Sort'),
                        ('Cây nhị phân tìm kiếm (BST) có tính chất gì?', 'c', 'Node trái > Node phải', 'Node phải < Node gốc', 'Node trái < Node gốc < Node phải', 'Tất cả node bằng nhau'),
                        ('Quick Sort chọn gì để chia mảng?', 'b', 'Phần tử đầu tiên luôn', 'Pivot (phần tử chốt)', 'Phần tử giữa luôn', 'Phần tử ngẫu nhiên luôn'),
                        ('Độ phức tạp tốt nhất của Merge Sort?', 'c', 'O(n²)', 'O(n)', 'O(n log n)', 'O(log n)'),
                        ('Hash Table có độ phức tạp trung bình để tìm kiếm là?', 'a', 'O(1)', 'O(n)', 'O(log n)', 'O(n²)'),
                    ]
                }
            },
            # Kinh tế
            {
                'title': 'Kế toán tài chính cơ bản',
                'cat': 'kinh-te', 'instructor': gv2, 'price': 199000, 'level': 'beginner',
                'desc': 'Học các nguyên tắc kế toán cơ bản, lập báo cáo tài chính, ghi nhận bút toán và phân tích báo cáo doanh nghiệp.',
                'obj': 'Hiểu nguyên tắc kế toán kép\nLập được bảng cân đối kế toán\nGhi nhận và phân loại bút toán\nĐọc hiểu báo cáo tài chính',
                'req': 'Không cần kinh nghiệm kế toán\nBiết toán cơ bản',
                'hours': 20,
                'chapters': [
                    ('Chương 1: Nguyên lý kế toán', [
                        ('Kế toán là gì? Phương trình kế toán', 'https://www.youtube.com/embed/yYX4bvQSqbo', 20),
                        ('Tài khoản kế toán và Bút toán kép', 'https://www.youtube.com/embed/7abKkCcHfSE', 25),
                        ('Chu kỳ kế toán và Nhật ký kế toán', 'https://www.youtube.com/embed/PfxT1t7JCsU', 22),
                    ]),
                    ('Chương 2: Báo cáo tài chính', [
                        ('Bảng cân đối kế toán (Balance Sheet)', 'https://www.youtube.com/embed/d5lGALbzLIA', 28),
                        ('Báo cáo kết quả kinh doanh (P&L)', 'https://www.youtube.com/embed/K0MQ6Zl-EM0', 25),
                        ('Báo cáo lưu chuyển tiền tệ', 'https://www.youtube.com/embed/JOJ_A-HEy1U', 20),
                    ]),
                ],
                'exam': {
                    'title': 'Kiểm tra Kế toán tài chính',
                    'duration': 20, 'pass_score': 60,
                    'questions': [
                        ('Phương trình kế toán cơ bản là gì?', 'a', 'Tài sản = Nợ phải trả + Vốn chủ sở hữu', 'Doanh thu = Chi phí + Lợi nhuận', 'Tài sản = Doanh thu - Chi phí', 'Vốn = Tài sản - Lợi nhuận'),
                        ('Bút toán kép có nghĩa là gì?', 'b', 'Ghi 2 lần vào cùng tài khoản', 'Mỗi nghiệp vụ ghi Nợ 1 TK và Có 1 TK', 'Sử dụng 2 quyển sổ', 'Kiểm tra 2 lần'),
                        ('Tài sản ngắn hạn là gì?', 'a', 'Tài sản chuyển đổi thành tiền trong 12 tháng', 'Tài sản cố định', 'Đầu tư dài hạn', 'Tài sản vô hình'),
                        ('Khấu hao tài sản cố định được ghi nhận như thế nào?', 'c', 'Tăng tài sản', 'Giảm nợ phải trả', 'Tăng chi phí, giảm tài sản', 'Tăng vốn chủ'),
                        ('Balance Sheet (Bảng CĐKT) thể hiện điều gì?', 'b', 'Doanh thu và chi phí', 'Tình hình tài chính tại một thời điểm', 'Lưu chuyển tiền tệ', 'Kế hoạch kinh doanh'),
                        ('Doanh nghiệp có lãi khi?', 'a', 'Doanh thu > Tổng chi phí', 'Tài sản > Nợ phải trả', 'Tiền mặt tăng', 'Vốn góp tăng'),
                        ('Công nợ phải thu (Accounts Receivable) là?', 'b', 'Tiền doanh nghiệp nợ NCC', 'Tiền khách hàng còn nợ doanh nghiệp', 'Chi phí trả trước', 'Thuế phải nộp'),
                        ('Chi phí khấu hao là chi phí gì?', 'c', 'Chi phí bằng tiền', 'Chi phí trực tiếp', 'Chi phí phi tiền mặt', 'Chi phí biến đổi'),
                    ]
                }
            },
            {
                'title': 'Marketing căn bản và Digital Marketing',
                'cat': 'kinh-te', 'instructor': gv3, 'price': 249000, 'level': 'beginner',
                'desc': 'Học Marketing Mix 4P, nghiên cứu thị trường, xây dựng chiến lược marketing số, SEO, Social Media và quảng cáo Google/Facebook.',
                'obj': 'Hiểu Marketing Mix 4P\nPhân tích thị trường SWOT\nChạy quảng cáo Facebook/Google\nXây dựng chiến lược Digital Marketing',
                'req': 'Không yêu cầu kinh nghiệm\nCó smartphone hoặc máy tính',
                'hours': 25,
                'chapters': [
                    ('Chương 1: Marketing cơ bản', [
                        ('Marketing là gì? Marketing Mix 4P', 'https://www.youtube.com/embed/nIe0sJmRHgs', 18),
                        ('Phân tích SWOT và nghiên cứu thị trường', 'https://www.youtube.com/embed/Jv3QHW0MfmE', 20),
                        ('Hành vi người tiêu dùng', 'https://www.youtube.com/embed/Qp8JBckBz3I', 15),
                    ]),
                    ('Chương 2: Digital Marketing', [
                        ('SEO - Tối ưu công cụ tìm kiếm', 'https://www.youtube.com/embed/hF515-0Tduk', 25),
                        ('Facebook Ads - Quảng cáo Facebook', 'https://www.youtube.com/embed/GBk1R0gCeFk', 30),
                        ('Google Ads và Email Marketing', 'https://www.youtube.com/embed/IIRaCAU3JjM', 28),
                    ]),
                ],
                'exam': {
                    'title': 'Kiểm tra Marketing',
                    'duration': 20, 'pass_score': 60,
                    'questions': [
                        ('Marketing Mix 4P gồm những yếu tố nào?', 'a', 'Product, Price, Place, Promotion', 'People, Process, Physical, Performance', 'Plan, Price, Place, People', 'Product, Profit, Place, People'),
                        ('SWOT phân tích những yếu tố gì?', 'b', 'Sale, Work, Output, Target', 'Strengths, Weaknesses, Opportunities, Threats', 'Strategy, Work, Operation, Tactic', 'System, Work, Organization, Team'),
                        ('SEO là viết tắt của gì?', 'c', 'Social Engagement Optimization', 'Service Engine Online', 'Search Engine Optimization', 'Site Engagement Output'),
                        ('KPI trong Marketing là gì?', 'a', 'Key Performance Indicator', 'Key Product Information', 'Key Price Index', 'Knowledge Performance Input'),
                        ('Target audience là gì?', 'b', 'Mục tiêu doanh thu', 'Đối tượng khách hàng mục tiêu', 'Chiến lược giá', 'Kênh phân phối'),
                    ]
                }
            },
            # Ngôn ngữ Anh
            {
                'title': 'Tiếng Anh giao tiếp từ mất gốc',
                'cat': 'ngon-ngu', 'instructor': gv2, 'price': 0, 'level': 'beginner',
                'desc': 'Khóa học tiếng Anh giao tiếp miễn phí từ con số 0. Học phát âm chuẩn, ngữ pháp cơ bản, từ vựng hàng ngày và hội thoại thực tế.',
                'obj': 'Phát âm đúng chuẩn IPA\nGiao tiếp tình huống hàng ngày\nNắm vững ngữ pháp cơ bản\nNghe hiểu tiếng Anh native',
                'req': 'Không yêu cầu gì cả\nCó tai nghe để luyện phát âm',
                'hours': 30,
                'chapters': [
                    ('Chương 1: Phát âm & Bảng chữ cái', [
                        ('Bảng chữ cái và phát âm tiếng Anh', 'https://www.youtube.com/embed/GN-9B2-9LPA', 15),
                        ('Nguyên âm và phụ âm IPA', 'https://www.youtube.com/embed/dKL0LLs1Wss', 20),
                        ('Trọng âm và ngữ điệu câu', 'https://www.youtube.com/embed/7zEYzVuPvHk', 18),
                    ]),
                    ('Chương 2: Ngữ pháp nền tảng', [
                        ('Thì hiện tại đơn và hiện tại tiếp diễn', 'https://www.youtube.com/embed/BEQEy7APbDQ', 22),
                        ('Thì quá khứ đơn và quá khứ tiếp diễn', 'https://www.youtube.com/embed/AUTdBW-JhLU', 25),
                        ('Câu hỏi Yes/No và Wh-questions', 'https://www.youtube.com/embed/5PiGnJODxNM', 20),
                    ]),
                    ('Chương 3: Giao tiếp thực tế', [
                        ('Chào hỏi và giới thiệu bản thân', 'https://www.youtube.com/embed/E4NU3O2DPEM', 15),
                        ('Mua sắm và hỏi đường', 'https://www.youtube.com/embed/2v8vilFXNSo', 18),
                        ('Phỏng vấn xin việc bằng tiếng Anh', 'https://www.youtube.com/embed/HG68Ymazo18', 25),
                    ]),
                ],
                'exam': {
                    'title': 'Kiểm tra Tiếng Anh giao tiếp',
                    'duration': 20, 'pass_score': 60,
                    'questions': [
                        ('What is the correct sentence?', 'a', 'She goes to school every day', 'She go to school every day', 'She going to school every day', 'She goed to school every day'),
                        ('Chọn câu trả lời đúng cho "Where are you from?"', 'c', 'I am fine', 'I am 20 years old', 'I am from Vietnam', 'I go to school'),
                        ('Thì hiện tại hoàn thành dùng trong trường hợp nào?', 'b', 'Hành động đang xảy ra', 'Hành động đã xảy ra và ảnh hưởng đến hiện tại', 'Hành động tương lai', 'Hành động thói quen'),
                        ('Câu "I have been studying for 2 hours" dùng thì gì?', 'c', 'Present Simple', 'Present Continuous', 'Present Perfect Continuous', 'Past Perfect'),
                        ('"Could you repeat that, please?" dùng để làm gì?', 'a', 'Yêu cầu nói lại', 'Từ chối lịch sự', 'Hỏi thông tin', 'Xin phép'),
                    ]
                }
            },
            # Đại cương - môn bắt buộc
            {
                'title': 'Toán cao cấp A1 - Giải tích',
                'cat': 'co-so', 'instructor': gv3, 'price': 0, 'level': 'beginner',
                'desc': 'Giải tích hàm một biến: giới hạn, đạo hàm, tích phân. Bài tập đầy đủ theo đề cương ĐH Bình Dương, có giải chi tiết.',
                'obj': 'Tính giới hạn hàm số\nTính đạo hàm các loại hàm\nTính tích phân bất định và xác định\nÁp dụng giải bài toán thực tế',
                'req': 'Toán THPT\nKiến thức hàm số cơ bản',
                'hours': 40,
                'chapters': [
                    ('Chương 1: Giới hạn và Liên tục', [
                        ('Giới hạn hàm số - Khái niệm và định lý', 'https://www.youtube.com/embed/riXcZT2ICjA', 30),
                        ('Các dạng vô định và L\'Hopital', 'https://www.youtube.com/embed/kfF40MiS7zA', 25),
                        ('Hàm số liên tục', 'https://www.youtube.com/embed/joewHl1CCjM', 20),
                    ]),
                    ('Chương 2: Đạo hàm và Vi phân', [
                        ('Đạo hàm - Định nghĩa và quy tắc tính', 'https://www.youtube.com/embed/rAof9Ld5sOg', 35),
                        ('Đạo hàm hàm hợp và hàm ngược', 'https://www.youtube.com/embed/HfACrKJ_Y2w', 30),
                        ('Ứng dụng đạo hàm - Cực trị và đồ thị', 'https://www.youtube.com/embed/5yfh5cf4-0o', 35),
                    ]),
                    ('Chương 3: Tích phân', [
                        ('Tích phân bất định và công thức', 'https://www.youtube.com/embed/rfG8ce4nNh0', 30),
                        ('Tích phân xác định - Định lý Newton-Leibniz', 'https://www.youtube.com/embed/FnJqaIESC2s', 35),
                        ('Ứng dụng tích phân tính diện tích', 'https://www.youtube.com/embed/8B31SAk1nok', 30),
                    ]),
                ],
                'exam': {
                    'title': 'Kiểm tra Toán cao cấp A1',
                    'duration': 45, 'pass_score': 50,
                    'questions': [
                        ('Giới hạn lim(x→0) sin(x)/x bằng bao nhiêu?', 'a', '1', '0', 'Vô cực', 'Không xác định'),
                        ('Đạo hàm của f(x) = x³ là?', 'b', 'x²', '3x²', '3x', 'x⁴/4'),
                        ('Đạo hàm của f(x) = e^x là?', 'a', 'e^x', 'xe^(x-1)', 'e^(x-1)', 'ln(x)'),
                        ('Tích phân ∫x² dx bằng?', 'c', 'x²/2 + C', '2x + C', 'x³/3 + C', 'x³ + C'),
                        ('Quy tắc L\'Hopital dùng khi nào?', 'b', 'Giới hạn cho kết quả xác định', 'Giới hạn cho dạng vô định 0/0 hoặc ∞/∞', 'Đạo hàm không tồn tại', 'Hàm không liên tục'),
                        ('Hàm số f(x) = |x| có đạo hàm tại x=0 không?', 'c', 'Có, bằng 0', 'Có, bằng 1', 'Không có đạo hàm tại x=0', 'Có, bằng -1'),
                        ('Diện tích hình phẳng giới hạn bởi đường cong tính bằng?', 'a', 'Tích phân xác định của giá trị tuyệt đối', 'Tích phân bất định', 'Đạo hàm của hàm số', 'Giới hạn của hàm số'),
                        ('Điểm cực đại của hàm số khi?', 'b', 'f\'(x) = 0', 'f\'(x) = 0 và f\'\'(x) < 0', 'f\'\'(x) = 0', 'f(x) đạt giá trị lớn nhất'),
                    ]
                }
            },
            {
                'title': 'Vật lý đại cương - Cơ học và Nhiệt học',
                'cat': 'co-so', 'instructor': gv3, 'price': 0, 'level': 'beginner',
                'desc': 'Vật lý đại cương chương trình ĐH: Cơ học Newton, động lực học, năng lượng, nhiệt động lực học. Bài tập có lời giải chi tiết.',
                'obj': 'Áp dụng định luật Newton\nGiải bài toán động lực học\nTính toán năng lượng và công\nHiểu nguyên lý nhiệt động học',
                'req': 'Toán THPT\nVật lý THPT cơ bản',
                'hours': 35,
                'chapters': [
                    ('Chương 1: Cơ học Newton', [
                        ('Ba định luật Newton', 'https://www.youtube.com/embed/kKKM8Y-u7ds', 25),
                        ('Các lực cơ học: ma sát, lực đàn hồi', 'https://www.youtube.com/embed/aE7WbyWEGqc', 22),
                        ('Chuyển động tròn và lực hướng tâm', 'https://www.youtube.com/embed/6kxhTCMCn4M', 20),
                    ]),
                    ('Chương 2: Năng lượng và Động lượng', [
                        ('Công và năng lượng', 'https://www.youtube.com/embed/w4QFJb9a8vo', 20),
                        ('Bảo toàn năng lượng', 'https://www.youtube.com/embed/Ez1olV9Kkzk', 25),
                        ('Động lượng và va chạm', 'https://www.youtube.com/embed/XFhntPxow0U', 22),
                    ]),
                ],
                'exam': {
                    'title': 'Kiểm tra Vật lý đại cương',
                    'duration': 30, 'pass_score': 50,
                    'questions': [
                        ('Định luật II Newton phát biểu?', 'a', 'F = ma (Lực = Khối lượng × Gia tốc)', 'F = mv (Lực = Khối lượng × Vận tốc)', 'F = mgh', 'F = kx'),
                        ('Đơn vị của công suất trong hệ SI?', 'b', 'Joule (J)', 'Watt (W)', 'Newton (N)', 'Pascal (Pa)'),
                        ('Bảo toàn năng lượng nói gì?', 'c', 'Năng lượng luôn giảm', 'Năng lượng luôn tăng', 'Năng lượng không tự sinh ra hoặc mất đi', 'Năng lượng bằng khối lượng'),
                        ('Gia tốc rơi tự do g ≈ ?', 'a', '9.8 m/s²', '10 m/s', '9.8 m/s', '10 m/s²'),
                        ('Động lượng được tính bằng?', 'b', 'p = ma', 'p = mv', 'p = Ft', 'p = ½mv²'),
                    ]
                }
            },
        ]

        created_courses = []
        for cd in courses_data:
            slug = slugify(cd['title'].replace('đ','d').replace('ề','e').replace('ạ','a')) + '-' + str(uuid.uuid4())[:6]
            course, created = Course.objects.get_or_create(
                title=cd['title'],
                defaults={
                    'slug': slug,
                    'instructor': cd['instructor'],
                    'category': cats[cd['cat']],
                    'description': cd['desc'],
                    'price': cd['price'],
                    'level': cd['level'],
                    'status': 'published',
                    'duration_hours': cd['hours'],
                    'requirements': cd['req'],
                    'objectives': cd['obj'],
                }
            )
            if created:
                for ci, (chapter_title, lessons) in enumerate(cd['chapters'], 1):
                    chapter = Chapter.objects.create(course=course, title=chapter_title, order=ci)
                    for li, (lesson_title, video_url, duration) in enumerate(lessons, 1):
                        Lesson.objects.create(
                            chapter=chapter, title=lesson_title,
                            content_type='video', video_url=video_url,
                            duration=duration, order=li, is_preview=(li == 1),
                            content=f'Nội dung bài học: {lesson_title}'
                        )
                # Tạo đề thi
                exam = Exam.objects.create(
                    course=course,
                    title=cd['exam']['title'],
                    description='Bài kiểm tra đánh giá kiến thức tổng quát',
                    duration_minutes=cd['exam']['duration'],
                    total_questions=len(cd['exam']['questions']),
                    pass_score=cd['exam']['pass_score'],
                    is_random=True, is_active=True
                )
                for qi, (content, correct, a, b, c, d) in enumerate(cd['exam']['questions'], 1):
                    Question.objects.create(
                        exam=exam, content=content,
                        question_type='multiple_choice',
                        option_a=a, option_b=b, option_c=c, option_d=d,
                        correct_answer=correct, points=1, order=qi
                    )
            created_courses.append(course)

        self.stdout.write('✅ Courses, Lessons, Exams done')

        # Enrollments & Reviews
        for sv in [sv1, sv2, sv3]:
            for course in created_courses[:4]:
                Enrollment.objects.get_or_create(student=sv, course=course, defaults={'progress': 0})

        reviews_data = [
            (sv1, created_courses[0], 5, 'Khóa Python rất hay, giảng viên giải thích dễ hiểu! Video chất lượng cao.'),
            (sv2, created_courses[0], 4, 'Nội dung tốt, cần thêm bài tập thực hành nhiều hơn.'),
            (sv1, created_courses[1], 5, 'Django Framework tuyệt vời! Học xong làm được dự án thật.'),
            (sv3, created_courses[2], 5, 'SQL rất quan trọng, khóa này giúp em hiểu database sâu hơn.'),
            (sv2, created_courses[3], 4, 'CTDL và Giải thuật khó nhưng thầy giải thích rõ ràng.'),
        ]
        for sv, course, rating, comment in reviews_data:
            Review.objects.get_or_create(
                course=course, student=sv,
                defaults={'rating': rating, 'comment': comment}
            )

        self.stdout.write(self.style.SUCCESS('''
╔══════════════════════════════════════════════════╗
║   ✅ SEED DATA THẬT HOÀN TẤT!                   ║
╠══════════════════════════════════════════════════╣
║  8 khóa học thật (Python, Django, SQL, CTDL...) ║
║  Video YouTube thật trong mỗi bài học            ║
║  Đề thi thật với câu hỏi chi tiết               ║
║  8 danh mục theo khoa ĐH Bình Dương             ║
╠══════════════════════════════════════════════════╣
║ Admin:  admin@elearning.com / Admin@123          ║
║ GV:     gv1@elearning.com  / Gv@123456          ║
║ SV:     sv1@elearning.com  / Sv@123456          ║
╚══════════════════════════════════════════════════╝
        '''))

    def _user(self, email, full_name, role, password):
        username = email.split('@')[0]
        user, created = User.objects.get_or_create(email=email, defaults={
            'username': username, 'full_name': full_name, 'role': role,
            'phone': '0901234567', 'is_active': True,
        })
        if created:
            user.set_password(password)
            if role == 'admin':
                user.is_staff = True
                user.is_superuser = True
            user.save()
        return user

    def _cat(self, name, slug, icon):
        cat, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name, 'icon': icon, 'description': f'Danh mục {name}'})
        return cat
