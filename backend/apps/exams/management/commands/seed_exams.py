"""
Management command: seed_exams
Tự động tạo đề thi trắc nghiệm cho mỗi khóa học nếu chưa có.
Câu hỏi được xây dựng sẵn theo từng môn học phổ biến.
"""
from django.core.management.base import BaseCommand
from apps.courses.models import Course
from apps.exams.models import Exam, Question


# ── Ngân hàng câu hỏi theo từ khóa môn học ──────────────────────────
QUESTION_BANK = {
    'cấu trúc dữ liệu': [
        {
            'content': 'Cấu trúc dữ liệu Stack hoạt động theo nguyên tắc nào?',
            'option_a': 'FIFO - First In First Out',
            'option_b': 'LIFO - Last In First Out',
            'option_c': 'Random - Ngẫu nhiên',
            'option_d': 'Priority - Ưu tiên',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'Độ phức tạp thời gian của thuật toán tìm kiếm nhị phân là bao nhiêu?',
            'option_a': 'O(1)',
            'option_b': 'O(n)',
            'option_c': 'O(log n)',
            'option_d': 'O(n²)',
            'correct_answer': 'C',
            'type': 'multiple_choice',
        },
        {
            'content': 'Queue là cấu trúc dữ liệu hoạt động theo nguyên tắc FIFO.',
            'option_a': 'Đúng',
            'option_b': 'Sai',
            'correct_answer': 'A',
            'type': 'true_false',
        },
        {
            'content': 'Thuật toán sắp xếp nào có độ phức tạp trung bình tốt nhất O(n log n)?',
            'option_a': 'Bubble Sort',
            'option_b': 'Selection Sort',
            'option_c': 'Quick Sort',
            'option_d': 'Insertion Sort',
            'correct_answer': 'C',
            'type': 'multiple_choice',
        },
        {
            'content': 'Trong cây nhị phân tìm kiếm (BST), giá trị nút con trái luôn _____ giá trị nút cha.',
            'option_a': 'Lớn hơn',
            'option_b': 'Nhỏ hơn hoặc bằng',
            'option_c': 'Bằng',
            'option_d': 'Không liên quan',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'Phương pháp duyệt cây nào duyệt theo thứ tự: Trái → Gốc → Phải?',
            'option_a': 'Pre-order',
            'option_b': 'In-order',
            'option_c': 'Post-order',
            'option_d': 'Level-order',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'Linked List có thể truy cập phần tử theo chỉ số (index) với độ phức tạp O(1).',
            'option_a': 'Đúng',
            'option_b': 'Sai',
            'correct_answer': 'B',
            'type': 'true_false',
        },
        {
            'content': 'Bubble Sort có độ phức tạp thời gian trong trường hợp xấu nhất là?',
            'option_a': 'O(n)',
            'option_b': 'O(n log n)',
            'option_c': 'O(n²)',
            'option_d': 'O(log n)',
            'correct_answer': 'C',
            'type': 'multiple_choice',
        },
        {
            'content': 'Cấu trúc dữ liệu nào phù hợp nhất để cài đặt thuật toán BFS (Breadth-First Search)?',
            'option_a': 'Stack',
            'option_b': 'Queue',
            'option_c': 'Tree',
            'option_d': 'Heap',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'Độ phức tạp không gian (Space Complexity) của Merge Sort là?',
            'option_a': 'O(1)',
            'option_b': 'O(log n)',
            'option_c': 'O(n)',
            'option_d': 'O(n²)',
            'correct_answer': 'C',
            'type': 'multiple_choice',
        },
    ],
    'lập trình hướng đối tượng': [
        {
            'content': 'Tính chất nào của OOP cho phép một lớp con kế thừa thuộc tính và phương thức từ lớp cha?',
            'option_a': 'Encapsulation (Đóng gói)',
            'option_b': 'Inheritance (Kế thừa)',
            'option_c': 'Polymorphism (Đa hình)',
            'option_d': 'Abstraction (Trừu tượng)',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'Interface trong Java có thể chứa phương thức có thân hàm (body) không?',
            'option_a': 'Đúng - từ Java 8 trở lên (default methods)',
            'option_b': 'Sai - Interface không bao giờ có thân hàm',
            'correct_answer': 'A',
            'type': 'true_false',
        },
        {
            'content': 'Từ khóa nào trong Java dùng để ngăn không cho lớp con ghi đè phương thức?',
            'option_a': 'static',
            'option_b': 'private',
            'option_c': 'final',
            'option_d': 'abstract',
            'correct_answer': 'C',
            'type': 'multiple_choice',
        },
        {
            'content': 'Polymorphism (Đa hình) trong OOP có nghĩa là?',
            'option_a': 'Một lớp có nhiều constructor',
            'option_b': 'Cùng tên phương thức nhưng hành vi khác nhau tùy đối tượng',
            'option_c': 'Ẩn thuộc tính của đối tượng',
            'option_d': 'Kế thừa từ nhiều lớp cha',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'Constructor là gì trong OOP?',
            'option_a': 'Phương thức dùng để hủy đối tượng',
            'option_b': 'Phương thức đặc biệt được gọi khi tạo đối tượng mới',
            'option_c': 'Thuộc tính tĩnh của lớp',
            'option_d': 'Phương thức trả về giá trị boolean',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'Encapsulation (Đóng gói) trong OOP nhằm mục đích gì?',
            'option_a': 'Tăng tốc độ thực thi chương trình',
            'option_b': 'Che giấu dữ liệu và bảo vệ trạng thái bên trong đối tượng',
            'option_c': 'Cho phép kế thừa đa cấp',
            'option_d': 'Tạo nhiều đối tượng từ một lớp',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'Lớp Abstract (abstract class) trong Java có thể được khởi tạo trực tiếp.',
            'option_a': 'Đúng',
            'option_b': 'Sai',
            'correct_answer': 'B',
            'type': 'true_false',
        },
        {
            'content': 'Design Pattern nào thuộc nhóm Creational Pattern?',
            'option_a': 'Observer',
            'option_b': 'Singleton',
            'option_c': 'Strategy',
            'option_d': 'Decorator',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'Overloading (Nạp chồng) và Overriding (Ghi đè) khác nhau ở điểm nào?',
            'option_a': 'Overloading cùng tên, khác tham số; Overriding cùng tên, cùng tham số ở lớp con',
            'option_b': 'Overloading là kế thừa; Overriding là đóng gói',
            'option_c': 'Chúng giống nhau hoàn toàn',
            'option_d': 'Overloading chỉ có trong C++',
            'correct_answer': 'A',
            'type': 'multiple_choice',
        },
        {
            'content': 'Từ khóa "this" trong Java dùng để chỉ?',
            'option_a': 'Lớp cha hiện tại',
            'option_b': 'Đối tượng hiện tại của lớp',
            'option_c': 'Constructor mặc định',
            'option_d': 'Phương thức tĩnh',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
    ],
    'mạng máy tính': [
        {
            'content': 'Mô hình OSI có bao nhiêu tầng?',
            'option_a': '5',
            'option_b': '6',
            'option_c': '7',
            'option_d': '4',
            'correct_answer': 'C',
            'type': 'multiple_choice',
        },
        {
            'content': 'Giao thức TCP thuộc tầng nào trong mô hình OSI?',
            'option_a': 'Tầng Network (Mạng)',
            'option_b': 'Tầng Transport (Vận chuyển)',
            'option_c': 'Tầng Application (Ứng dụng)',
            'option_d': 'Tầng Data Link (Liên kết dữ liệu)',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'Địa chỉ IP 192.168.1.1 thuộc lớp địa chỉ nào?',
            'option_a': 'Lớp A',
            'option_b': 'Lớp B',
            'option_c': 'Lớp C',
            'option_d': 'Lớp D',
            'correct_answer': 'C',
            'type': 'multiple_choice',
        },
        {
            'content': 'DNS (Domain Name System) có chức năng gì?',
            'option_a': 'Mã hóa dữ liệu truyền tải',
            'option_b': 'Chuyển đổi tên miền thành địa chỉ IP',
            'option_c': 'Phân phối địa chỉ IP động',
            'option_d': 'Định tuyến gói tin',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'TCP đảm bảo truyền dữ liệu tin cậy, còn UDP thì không.',
            'option_a': 'Đúng',
            'option_b': 'Sai',
            'correct_answer': 'A',
            'type': 'true_false',
        },
        {
            'content': 'Port mặc định của giao thức HTTPS là?',
            'option_a': '80',
            'option_b': '443',
            'option_c': '8080',
            'option_d': '22',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'Thiết bị nào hoạt động ở tầng Network (Layer 3) của mô hình OSI?',
            'option_a': 'Hub',
            'option_b': 'Switch',
            'option_c': 'Router',
            'option_d': 'Repeater',
            'correct_answer': 'C',
            'type': 'multiple_choice',
        },
        {
            'content': 'Subnet mask 255.255.255.0 tương đương với ký hiệu CIDR nào?',
            'option_a': '/16',
            'option_b': '/24',
            'option_c': '/8',
            'option_d': '/32',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'DHCP có chức năng gì trong mạng máy tính?',
            'option_a': 'Phân giải tên miền',
            'option_b': 'Cấp phát địa chỉ IP tự động cho thiết bị',
            'option_c': 'Bảo mật kết nối mạng',
            'option_d': 'Định tuyến gói tin giữa các mạng',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'Giao thức ARP (Address Resolution Protocol) dùng để làm gì?',
            'option_a': 'Tìm địa chỉ IP từ tên miền',
            'option_b': 'Tìm địa chỉ MAC từ địa chỉ IP',
            'option_c': 'Phân phối địa chỉ IP',
            'option_d': 'Mã hóa dữ liệu',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
    ],
    'cơ sở dữ liệu': [
        {
            'content': 'Dạng chuẩn (Normal Form) nào yêu cầu bảng không có phụ thuộc hàm một phần?',
            'option_a': '1NF',
            'option_b': '2NF',
            'option_c': '3NF',
            'option_d': 'BCNF',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'Lệnh SQL nào dùng để xóa toàn bộ dữ liệu trong bảng nhưng giữ lại cấu trúc bảng?',
            'option_a': 'DROP TABLE',
            'option_b': 'DELETE FROM table_name',
            'option_c': 'TRUNCATE TABLE',
            'option_d': 'REMOVE TABLE',
            'correct_answer': 'C',
            'type': 'multiple_choice',
        },
        {
            'content': 'PRIMARY KEY trong SQL có thể chứa giá trị NULL.',
            'option_a': 'Đúng',
            'option_b': 'Sai',
            'correct_answer': 'B',
            'type': 'true_false',
        },
        {
            'content': 'INNER JOIN trả về kết quả như thế nào?',
            'option_a': 'Tất cả bản ghi từ bảng trái',
            'option_b': 'Tất cả bản ghi từ bảng phải',
            'option_c': 'Chỉ những bản ghi khớp ở cả hai bảng',
            'option_d': 'Tất cả bản ghi từ cả hai bảng',
            'correct_answer': 'C',
            'type': 'multiple_choice',
        },
        {
            'content': 'Hàm COUNT(*) trong SQL đếm bao nhiêu?',
            'option_a': 'Số cột trong bảng',
            'option_b': 'Số bảng trong database',
            'option_c': 'Số hàng trong kết quả truy vấn (kể cả NULL)',
            'option_d': 'Số giá trị không NULL',
            'correct_answer': 'C',
            'type': 'multiple_choice',
        },
        {
            'content': 'Transaction trong CSDL phải đảm bảo các tính chất ACID. ACID là viết tắt của?',
            'option_a': 'Atomicity, Consistency, Isolation, Durability',
            'option_b': 'Access, Control, Index, Data',
            'option_c': 'Add, Create, Insert, Delete',
            'option_d': 'Availability, Concurrency, Integrity, Data',
            'correct_answer': 'A',
            'type': 'multiple_choice',
        },
        {
            'content': 'Index trong CSDL có tác dụng gì?',
            'option_a': 'Giảm dung lượng lưu trữ',
            'option_b': 'Tăng tốc độ truy vấn tìm kiếm',
            'option_c': 'Bảo mật dữ liệu',
            'option_d': 'Tự động sao lưu dữ liệu',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'VIEW trong SQL là gì?',
            'option_a': 'Bảng vật lý lưu dữ liệu',
            'option_b': 'Bảng ảo dựa trên kết quả của câu truy vấn SQL',
            'option_c': 'Thủ tục lưu trữ',
            'option_d': 'Ràng buộc dữ liệu',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'Lệnh GROUP BY thường đi kèm với hàm tổng hợp nào?',
            'option_a': 'WHERE',
            'option_b': 'ORDER BY',
            'option_c': 'HAVING',
            'option_d': 'Aggregate functions (SUM, COUNT, AVG...)',
            'correct_answer': 'D',
            'type': 'multiple_choice',
        },
        {
            'content': 'Khóa ngoại (Foreign Key) dùng để thiết lập quan hệ giữa hai bảng.',
            'option_a': 'Đúng',
            'option_b': 'Sai',
            'correct_answer': 'A',
            'type': 'true_false',
        },
    ],
    'lập trình web': [
        {
            'content': 'Thuộc tính nào trong HTML5 dùng để xác nhận trường input bắt buộc phải điền?',
            'option_a': 'validate',
            'option_b': 'required',
            'option_c': 'mandatory',
            'option_d': 'must-fill',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'CSS Box Model bao gồm các thành phần nào theo thứ tự từ trong ra ngoài?',
            'option_a': 'Content → Margin → Padding → Border',
            'option_b': 'Content → Padding → Border → Margin',
            'option_c': 'Padding → Content → Border → Margin',
            'option_d': 'Border → Padding → Content → Margin',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'JavaScript là ngôn ngữ lập trình đồng bộ (synchronous) hoàn toàn.',
            'option_a': 'Đúng',
            'option_b': 'Sai - JS có hỗ trợ bất đồng bộ qua callback, Promise, async/await',
            'correct_answer': 'B',
            'type': 'true_false',
        },
        {
            'content': 'Phương thức HTTP nào được dùng để cập nhật một phần tài nguyên?',
            'option_a': 'PUT',
            'option_b': 'POST',
            'option_c': 'PATCH',
            'option_d': 'UPDATE',
            'correct_answer': 'C',
            'type': 'multiple_choice',
        },
        {
            'content': 'CSS Flexbox property nào dùng để căn giữa các phần tử theo trục ngang?',
            'option_a': 'align-items: center',
            'option_b': 'justify-content: center',
            'option_c': 'text-align: center',
            'option_d': 'margin: auto',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'Cookie và LocalStorage khác nhau ở điểm chính nào?',
            'option_a': 'Cookie được gửi lên server mỗi request, LocalStorage thì không',
            'option_b': 'LocalStorage bảo mật hơn Cookie',
            'option_c': 'Cookie lưu được nhiều dữ liệu hơn',
            'option_d': 'Chúng giống nhau hoàn toàn',
            'correct_answer': 'A',
            'type': 'multiple_choice',
        },
        {
            'content': 'REST API trả về mã trạng thái HTTP nào khi tạo mới tài nguyên thành công?',
            'option_a': '200 OK',
            'option_b': '201 Created',
            'option_c': '204 No Content',
            'option_d': '202 Accepted',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'Event bubbling trong JavaScript là gì?',
            'option_a': 'Sự kiện lan từ phần tử con lên phần tử cha',
            'option_b': 'Sự kiện lan từ phần tử cha xuống phần tử con',
            'option_c': 'Sự kiện xảy ra đồng thời',
            'option_d': 'Sự kiện bị hủy',
            'correct_answer': 'A',
            'type': 'multiple_choice',
        },
        {
            'content': 'Semantic HTML element nào dùng để đánh dấu nội dung điều hướng?',
            'option_a': '<div class="nav">',
            'option_b': '<navigation>',
            'option_c': '<nav>',
            'option_d': '<menu>',
            'correct_answer': 'C',
            'type': 'multiple_choice',
        },
        {
            'content': 'CORS (Cross-Origin Resource Sharing) là gì?',
            'option_a': 'Một loại tấn công mạng',
            'option_b': 'Cơ chế cho phép/từ chối trình duyệt gọi API từ domain khác',
            'option_c': 'Giao thức truyền file',
            'option_d': 'Phương thức mã hóa dữ liệu',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
    ],
    'trí tuệ nhân tạo': [
        {
            'content': 'Supervised Learning (Học có giám sát) khác Unsupervised Learning ở điểm gì?',
            'option_a': 'Supervised dùng dữ liệu có nhãn, Unsupervised không có nhãn',
            'option_b': 'Supervised chạy nhanh hơn',
            'option_c': 'Unsupervised cần nhiều dữ liệu hơn',
            'option_d': 'Chúng giống nhau',
            'correct_answer': 'A',
            'type': 'multiple_choice',
        },
        {
            'content': 'Overfitting trong Machine Learning xảy ra khi?',
            'option_a': 'Mô hình học quá tốt trên training data nhưng kém trên test data',
            'option_b': 'Mô hình không học được gì từ dữ liệu',
            'option_c': 'Dữ liệu huấn luyện quá ít',
            'option_d': 'Tốc độ học (learning rate) quá thấp',
            'correct_answer': 'A',
            'type': 'multiple_choice',
        },
        {
            'content': 'Hàm kích hoạt ReLU trả về giá trị như thế nào?',
            'option_a': 'Luôn trả về giá trị từ 0 đến 1',
            'option_b': 'max(0, x) - trả về 0 nếu x âm, trả về x nếu x dương',
            'option_c': 'Luôn trả về -1 hoặc 1',
            'option_d': 'Trả về xác suất',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'Cross-Entropy Loss thường được dùng cho bài toán phân loại.',
            'option_a': 'Đúng',
            'option_b': 'Sai',
            'correct_answer': 'A',
            'type': 'true_false',
        },
        {
            'content': 'Thuật toán k-Means thuộc nhóm học máy nào?',
            'option_a': 'Supervised Learning',
            'option_b': 'Reinforcement Learning',
            'option_c': 'Unsupervised Learning',
            'option_d': 'Semi-supervised Learning',
            'correct_answer': 'C',
            'type': 'multiple_choice',
        },
        {
            'content': 'Gradient Descent là gì trong Machine Learning?',
            'option_a': 'Phương pháp đánh giá mô hình',
            'option_b': 'Thuật toán tối ưu hóa để cập nhật tham số mô hình',
            'option_c': 'Kỹ thuật chuẩn hóa dữ liệu',
            'option_d': 'Phương pháp phân chia dữ liệu',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'Convolutional Neural Network (CNN) thường được dùng cho bài toán nào?',
            'option_a': 'Xử lý ngôn ngữ tự nhiên',
            'option_b': 'Nhận dạng hình ảnh và thị giác máy tính',
            'option_c': 'Phân tích chuỗi thời gian',
            'option_d': 'Phân cụm dữ liệu',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'Dropout trong Deep Learning có tác dụng gì?',
            'option_a': 'Tăng tốc độ huấn luyện',
            'option_b': 'Ngăn overfitting bằng cách tắt ngẫu nhiên một số neuron khi training',
            'option_c': 'Giảm số lượng tham số mô hình',
            'option_d': 'Tăng độ chính xác trên training set',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'Precision và Recall là hai chỉ số đánh giá mô hình phân loại. F1-Score là?',
            'option_a': 'Trung bình cộng của Precision và Recall',
            'option_b': 'Trung bình điều hòa (harmonic mean) của Precision và Recall',
            'option_c': 'Tích của Precision và Recall',
            'option_d': 'Hiệu của Precision và Recall',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'Transfer Learning là kỹ thuật sử dụng mô hình đã được huấn luyện trước để giải quyết bài toán mới.',
            'option_a': 'Đúng',
            'option_b': 'Sai',
            'correct_answer': 'A',
            'type': 'true_false',
        },
    ],
    'default': [
        {
            'content': 'Ngôn ngữ lập trình nào được xem là "ngôn ngữ của Internet"?',
            'option_a': 'Python',
            'option_b': 'Java',
            'option_c': 'JavaScript',
            'option_d': 'C++',
            'correct_answer': 'C',
            'type': 'multiple_choice',
        },
        {
            'content': 'Git là công cụ quản lý phiên bản phân tán (Distributed Version Control System).',
            'option_a': 'Đúng',
            'option_b': 'Sai',
            'correct_answer': 'A',
            'type': 'true_false',
        },
        {
            'content': 'Lệnh Git nào dùng để lưu thay đổi vào repository?',
            'option_a': 'git save',
            'option_b': 'git push',
            'option_c': 'git commit',
            'option_d': 'git store',
            'correct_answer': 'C',
            'type': 'multiple_choice',
        },
        {
            'content': 'API là viết tắt của?',
            'option_a': 'Application Programming Interface',
            'option_b': 'Automated Program Integration',
            'option_c': 'Application Process Integration',
            'option_d': 'Advanced Programming Interface',
            'correct_answer': 'A',
            'type': 'multiple_choice',
        },
        {
            'content': 'Loại tấn công mạng nào cố gắng thử nhiều mật khẩu khác nhau cho đến khi tìm ra đúng?',
            'option_a': 'SQL Injection',
            'option_b': 'Phishing',
            'option_c': 'Brute Force',
            'option_d': 'XSS',
            'correct_answer': 'C',
            'type': 'multiple_choice',
        },
        {
            'content': 'RAM là bộ nhớ lưu trữ dữ liệu vĩnh viễn khi tắt máy.',
            'option_a': 'Đúng',
            'option_b': 'Sai - RAM là bộ nhớ tạm thời, mất dữ liệu khi tắt điện',
            'correct_answer': 'B',
            'type': 'true_false',
        },
        {
            'content': 'Hệ điều hành Linux thuộc dạng mã nguồn mở (open source).',
            'option_a': 'Đúng',
            'option_b': 'Sai',
            'correct_answer': 'A',
            'type': 'true_false',
        },
        {
            'content': 'JSON là viết tắt của?',
            'option_a': 'Java Standard Object Notation',
            'option_b': 'JavaScript Object Notation',
            'option_c': 'JavaScript Online Notation',
            'option_d': 'Java Simple Object Notation',
            'correct_answer': 'B',
            'type': 'multiple_choice',
        },
        {
            'content': 'Phương pháp Agile trong phát triển phần mềm tập trung vào?',
            'option_a': 'Tài liệu đầy đủ trước khi code',
            'option_b': 'Phân tích yêu cầu kỹ lưỡng trước',
            'option_c': 'Phát triển lặp, linh hoạt, phản hồi nhanh với thay đổi',
            'option_d': 'Lập kế hoạch cố định từ đầu đến cuối',
            'correct_answer': 'C',
            'type': 'multiple_choice',
        },
        {
            'content': 'Cloud Computing cho phép truy cập tài nguyên máy tính qua Internet theo mô hình dịch vụ.',
            'option_a': 'Đúng',
            'option_b': 'Sai',
            'correct_answer': 'A',
            'type': 'true_false',
        },
    ]
}


def get_questions_for_course(title: str):
    """Lấy câu hỏi phù hợp với môn học dựa trên tên khóa học."""
    title_lower = title.lower()
    for keyword, questions in QUESTION_BANK.items():
        if keyword == 'default':
            continue
        if keyword in title_lower:
            return questions
    return QUESTION_BANK['default']


class Command(BaseCommand):
    help = 'Tạo đề thi mẫu cho các khóa học chưa có bài thi'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Tạo lại đề thi dù đã có')
        parser.add_argument('--course-id', type=int, help='Chỉ tạo cho 1 khóa học cụ thể')

    def handle(self, *args, **options):
        courses = Course.objects.filter(status='published')
        if options.get('course_id'):
            courses = courses.filter(pk=options['course_id'])

        created_count = 0
        skipped_count = 0

        for course in courses:
            existing = Exam.objects.filter(course=course).count()
            if existing > 0 and not options.get('force'):
                skipped_count += 1
                self.stdout.write(f'  Bỏ qua: {course.title} (đã có {existing} đề thi)')
                continue

            questions_data = get_questions_for_course(course.title)

            # Tạo 2 đề thi: trắc nghiệm + ôn tập
            exams_to_create = [
                {
                    'title': f'Bài kiểm tra giữa kỳ - {course.title}',
                    'description': 'Đề thi trắc nghiệm kiểm tra kiến thức cơ bản của môn học.',
                    'duration_minutes': 30,
                    'pass_score': 50,
                    'questions': questions_data[:7],  # 7 câu đầu
                },
                {
                    'title': f'Bài kiểm tra cuối kỳ - {course.title}',
                    'description': 'Đề thi tổng hợp kiểm tra toàn bộ nội dung môn học.',
                    'duration_minutes': 45,
                    'pass_score': 60,
                    'questions': questions_data,  # Tất cả câu hỏi
                },
            ]

            for exam_info in exams_to_create:
                exam = Exam.objects.create(
                    course=course,
                    title=exam_info['title'],
                    description=exam_info['description'],
                    duration_minutes=exam_info['duration_minutes'],
                    total_questions=len(exam_info['questions']),
                    pass_score=exam_info['pass_score'],
                    is_random=True,
                    is_active=True,
                )

                for i, q_data in enumerate(exam_info['questions']):
                    Question.objects.create(
                        exam=exam,
                        content=q_data['content'],
                        question_type=q_data['type'],
                        option_a=q_data.get('option_a', ''),
                        option_b=q_data.get('option_b', ''),
                        option_c=q_data.get('option_c', ''),
                        option_d=q_data.get('option_d', ''),
                        correct_answer=q_data['correct_answer'],
                        points=1,
                        order=i + 1,
                    )

            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'  ✓ Tạo đề thi cho: {course.title} ({len(questions_data)} câu)')
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nHoàn thành! Tạo mới: {created_count} khóa học | Bỏ qua: {skipped_count} khóa học'
            )
        )
