import re
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions


# ── 170 Q&A tĩnh từ FAQ ───────────────────────────────────────────────
QA_LIST = [
    # Đăng Ký Tài Khoản
    ("đăng ký tài khoản mới", "Bạn truy cập trang chủ, nhấn nút 'Đăng ký', điền đầy đủ thông tin họ tên, email, mật khẩu rồi nhấn 'Hoàn tất'. Hệ thống sẽ gửi email xác nhận để kích hoạt tài khoản."),
    ("thông tin cần cung cấp khi đăng ký", "Bạn cần cung cấp: họ và tên, địa chỉ email hợp lệ, mật khẩu (tối thiểu 8 ký tự) và số điện thoại liên lạc."),
    ("không nhận được email xác nhận đăng ký", "Email có thể nằm trong thư mục Spam/Rác. Vui lòng kiểm tra và đánh dấu 'Không phải spam'. Nếu vẫn không thấy, nhấn 'Gửi lại email xác nhận' hoặc liên hệ hỗ trợ."),
    ("đăng ký bằng google facebook", "Hệ thống hỗ trợ đăng ký nhanh qua Google và Facebook. Chỉ cần nhấn nút tương ứng tại trang đăng ký và cấp quyền truy cập là xong."),
    ("tuổi tối thiểu đăng ký", "Người dùng phải từ 13 tuổi trở lên để tự đăng ký. Học viên dưới 18 tuổi cần có sự đồng ý của phụ huynh hoặc người giám hộ."),
    ("tạo nhiều tài khoản", "Mỗi người chỉ được tạo một tài khoản cá nhân. Việc tạo nhiều tài khoản vi phạm điều khoản sử dụng và có thể dẫn đến khóa tất cả các tài khoản liên quan."),
    ("xác minh email sau đăng ký", "Sau khi đăng ký, hệ thống gửi email chứa nút 'Xác minh tài khoản'. Nhấn vào nút đó để hoàn tất. Link có hiệu lực trong 24 giờ."),
    ("email đã tồn tại khi đăng ký", "Email này đã được dùng để đăng ký trước đó. Bạn thử chức năng 'Quên mật khẩu' để lấy lại quyền truy cập, hoặc dùng địa chỉ email khác."),
    ("đăng ký tài khoản mất phí không", "Hoàn toàn miễn phí! Việc tạo tài khoản không tốn bất kỳ chi phí nào. Phí chỉ phát sinh khi bạn đăng ký các khóa học có trả phí."),
    ("bắt đầu học sau đăng ký", "Sau khi xác minh email thành công, bạn có thể đăng nhập và bắt đầu khám phá các khóa học miễn phí ngay lập tức."),
    # Đăng Nhập
    ("không thể đăng nhập", "Vui lòng kiểm tra lại email và mật khẩu, đảm bảo không bật Caps Lock. Nếu quên mật khẩu, hãy dùng chức năng 'Quên mật khẩu'. Nếu vẫn không được, liên hệ bộ phận hỗ trợ."),
    ("tài khoản bị khóa sau đăng nhập sai", "Đây là biện pháp bảo mật tự động. Sau 5 lần nhập sai, tài khoản bị khóa tạm thời 30 phút. Bạn có thể đặt lại mật khẩu ngay để mở khóa sớm hơn."),
    ("đăng nhập nhiều thiết bị", "Có, bạn có thể đăng nhập đồng thời trên tối đa 3 thiết bị. Nếu vượt quá giới hạn, phiên đăng nhập cũ nhất sẽ tự động bị đăng xuất."),
    ("phiên đăng nhập hết hạn", "Phiên đăng nhập thông thường hết hạn sau 7 ngày không hoạt động. Nếu bật 'Ghi nhớ đăng nhập', thời gian kéo dài lên 30 ngày."),
    ("dữ liệu mất sau đăng xuất", "Không bao giờ! Toàn bộ tiến trình học, điểm số và bài tập của bạn được lưu trữ an toàn trên máy chủ."),
    ("đăng nhập thành công nhưng không thấy khóa học đã mua", "Hãy kiểm tra xem bạn đang đăng nhập đúng tài khoản dùng để mua không. Nếu đúng rồi, thử làm mới trang hoặc liên hệ hỗ trợ kèm mã đơn hàng."),
    # Quên Mật Khẩu
    ("lấy lại mật khẩu quên mật khẩu", "Tại trang đăng nhập, nhấn 'Quên mật khẩu', nhập email đăng ký và nhấn Gửi. Hệ thống sẽ gửi link đặt lại mật khẩu đến email của bạn trong vài phút."),
    ("không nhận được email đặt lại mật khẩu", "Kiểm tra thư mục Spam/Rác trước. Đảm bảo bạn nhập đúng email đăng ký. Nếu chờ quá 10 phút vẫn không thấy, hãy thử gửi lại hoặc liên hệ hỗ trợ."),
    ("link đặt lại mật khẩu hết hạn", "Link đặt lại mật khẩu có hiệu lực trong 1 giờ kể từ khi gửi. Nếu hết hạn, bạn cần quay lại trang 'Quên mật khẩu' để yêu cầu gửi link mới."),
    ("yêu cầu mật khẩu mới", "Mật khẩu cần tối thiểu 8 ký tự, bao gồm ít nhất 1 chữ hoa, 1 chữ thường, 1 số và 1 ký tự đặc biệt (@, #, $...)."),
    ("thay đổi mật khẩu khi đang đăng nhập", "Vào Cài đặt tài khoản → Bảo mật → Đổi mật khẩu. Nhập mật khẩu hiện tại và mật khẩu mới hai lần rồi nhấn Lưu."),
    ("quên cả email đăng ký", "Liên hệ bộ phận hỗ trợ qua live chat hoặc email, cung cấp họ tên, số điện thoại đăng ký. Đội ngũ sẽ xác minh và hỗ trợ khôi phục tài khoản."),
    # Hồ Sơ
    ("cập nhật thông tin hồ sơ cá nhân", "Nhấn vào ảnh đại diện góc trên bên phải → Hồ sơ của tôi → Chỉnh sửa. Cập nhật thông tin cần thiết và nhấn Lưu thay đổi."),
    ("thay đổi tên hiển thị", "Vào Hồ sơ cá nhân → Chỉnh sửa, thay đổi tên hiển thị và nhấn Lưu."),
    ("tải lên ảnh đại diện", "Vào Hồ sơ → Chỉnh sửa → nhấn vào vùng ảnh đại diện, chọn ảnh từ máy tính (JPG/PNG, tối đa 5MB), cắt ảnh và nhấn Lưu."),
    ("thay đổi email đăng ký", "Vào Cài đặt → Tài khoản → Đổi email, nhập email mới và xác minh qua link gửi đến email cũ."),
    ("xóa tài khoản", "Vào Cài đặt → Tài khoản → Xóa tài khoản và làm theo hướng dẫn. Lưu ý: hành động này không thể hoàn tác."),
    ("xem lịch sử học tập", "Vào Hồ sơ → Lịch sử học tập để xem danh sách khóa học đã tham gia, tiến trình hoàn thành, điểm số."),
    # Đăng Ký Khóa Học
    ("tìm kiếm đăng ký khóa học", "Dùng thanh tìm kiếm hoặc duyệt qua danh mục để tìm khóa học. Nhấn vào khóa học, xem chi tiết rồi nhấn 'Đăng ký ngay' để hoàn tất."),
    ("xem trước nội dung khóa học", "Có! Mỗi khóa học đều có phần giới thiệu miễn phí gồm mô tả, mục tiêu và 1-3 bài học mẫu để bạn trải nghiệm trước khi quyết định."),
    ("giới hạn số khóa học đăng ký", "Không giới hạn số lượng! Bạn có thể đăng ký và học song song nhiều khóa học tùy theo nhu cầu."),
    ("thời gian truy cập sau đăng ký", "Thông thường là trọn đời (lifetime access). Thông tin cụ thể được ghi rõ tại trang chi tiết khóa học."),
    ("yêu cầu kiến thức đầu vào khóa học", "Mỗi khóa học đều ghi rõ yêu cầu kiến thức đầu vào trong phần mô tả. Bạn nên đọc kỹ và thử bài học mẫu trước khi quyết định."),
    ("mã giảm giá voucher", "Tại trang thanh toán, bạn sẽ thấy ô 'Nhập mã giảm giá'. Điền mã và nhấn Áp dụng — hệ thống sẽ tự động tính toán số tiền được giảm."),
    # Thanh Toán
    ("phương thức thanh toán", "Hệ thống hỗ trợ: thẻ tín dụng/ghi nợ (Visa, Mastercard), chuyển khoản ngân hàng, ví điện tử (MoMo, ZaloPay, VNPay) và thanh toán qua QR Code."),
    ("thanh toán an toàn không", "Hoàn toàn an toàn! Mọi giao dịch được mã hóa SSL 256-bit và xử lý qua cổng thanh toán đạt chuẩn PCI DSS."),
    ("thanh toán thành công nhưng chưa mở được khóa học", "Vui lòng chờ 5-15 phút và làm mới trang. Nếu vẫn chưa mở, liên hệ hỗ trợ kèm ảnh chụp xác nhận giao dịch."),
    ("hóa đơn biên lai thanh toán", "Sau khi thanh toán thành công, hệ thống tự động gửi biên lai điện tử đến email đăng ký. Bạn cũng có thể xem tại mục Lịch sử giao dịch."),
    ("thanh toán trả góp", "Hệ thống hỗ trợ trả góp 0% lãi suất qua thẻ tín dụng của các ngân hàng liên kết (3, 6, 12 tháng)."),
    # Học Phí
    ("học phí tính như thế nào", "Học phí được định giá theo từng khóa học dựa trên độ dài, chất lượng nội dung và kinh nghiệm giảng viên. Giá hiển thị rõ trên trang chi tiết mỗi khóa học."),
    ("học viên mới có ưu đãi không", "Có! Học viên đăng ký lần đầu được giảm 20-30% cho khóa học đầu tiên."),
    ("học phí thay đổi sau khi đăng ký", "Không! Học phí bị khóa tại thời điểm bạn mua. Dù giá khóa học tăng sau đó, bạn vẫn được truy cập đầy đủ."),
    ("học bổng", "Có! Chúng tôi có quỹ học bổng hàng quý cho học viên xuất sắc và hoàn cảnh khó khăn. Liên hệ hỗ trợ để biết thêm chi tiết."),
    ("nội dung cập nhật có mất thêm phí không", "Không! Bạn chỉ trả một lần và nhận quyền truy cập tất cả nội dung cập nhật trong tương lai mà không phát sinh thêm chi phí."),
    # Bài Kiểm Tra
    ("bài kiểm tra có dạng như thế nào", "Bài kiểm tra có nhiều dạng: trắc nghiệm đơn/đa lựa chọn, điền vào chỗ trống và câu hỏi tự luận ngắn. Dạng cụ thể phụ thuộc vào từng khóa học."),
    ("làm lại bài kiểm tra", "Số lần làm lại tùy quy định của từng khóa học, thường từ 2-3 lần. Sau mỗi lần làm, hệ thống sẽ hiển thị phần bạn cần ôn lại."),
    ("thời gian làm bài kiểm tra", "Thời gian làm bài được quy định riêng cho từng bài kiểm tra, thường từ 15-60 phút. Đồng hồ đếm ngược hiển thị rõ ràng trong suốt quá trình làm bài."),
    ("điểm tối thiểu để qua bài kiểm tra", "Điểm qua thường là 60-70%, nhưng có thể khác tùy đề thi. Yêu cầu điểm tối thiểu được thông báo rõ ràng trước khi bạn bắt đầu làm bài."),
    ("xem lại đáp án sau khi nộp bài", "Tùy cài đặt của giảng viên. Một số bài kiểm tra cho xem đáp án ngay, số khác chỉ hiển thị điểm số."),
    ("mất kết nối internet khi làm bài", "Đừng lo! Hệ thống tự động lưu câu trả lời mỗi 30 giây. Khi kết nối lại, bạn có thể tiếp tục từ câu đã trả lời."),
    ("kết quả bài kiểm tra", "Bài trắc nghiệm chấm điểm và trả kết quả ngay lập tức sau khi nộp."),
    # Bài Tập
    ("bài tập chấm điểm tự động không", "Bài tập trắc nghiệm và lập trình được chấm tự động. Bài tập tự luận, đồ án cần giảng viên chấm thủ công."),
    ("nộp bài tập", "Vào bài học tương ứng → Bài tập → Làm bài. Điền câu trả lời hoặc tải file lên, kiểm tra lại và nhấn 'Nộp bài'."),
    ("bài tập có thời hạn không deadline", "Có! Mỗi bài tập đều hiển thị thời hạn nộp (deadline) rõ ràng. Hệ thống gửi nhắc nhở trước deadline 24 giờ qua email."),
    ("nộp bài tập trễ hạn", "Tùy quy định từng khóa. Một số khóa cho phép nộp trễ với mức trừ điểm. Kiểm tra quy định trong phần mô tả bài tập."),
    ("định dạng file nộp bài tập", "Hệ thống chấp nhận: PDF, DOCX, XLSX, PPTX, JPG, PNG, MP4 và file nén ZIP/RAR. Kích thước tối đa 50MB."),
    ("chỉnh sửa nộp lại bài tập", "Trước deadline, bạn có thể nộp lại nhiều lần — hệ thống ghi nhận lần nộp cuối cùng."),
    ("giảng viên có nhận xét bài tập không", "Có! Giảng viên thường cung cấp nhận xét chi tiết trong vòng 3-5 ngày làm việc sau deadline."),
    # Điểm Số
    ("xem điểm số tổng kết", "Vào trang khóa học → Tiến trình học tập → Điểm số. Tại đây hiển thị điểm từng bài tập, kiểm tra và điểm tổng kết."),
    ("điểm được tính như thế nào", "Thường: bài tập chiếm 40%, kiểm tra giữa kỳ 20%, kiểm tra cuối kỳ 40%. Có thể khác theo từng khóa."),
    ("điểm bao nhiêu được cấp chứng chỉ", "Cần đạt tối thiểu 70% (7/10 điểm) và hoàn thành ít nhất 80% nội dung khóa học để được cấp chứng chỉ."),
    ("phúc khảo điểm", "Trong vòng 7 ngày sau khi điểm được công bố, bạn có thể gửi yêu cầu phúc khảo qua mục Hỗ trợ."),
    ("tải bảng điểm", "Vào Hồ sơ → Thành tích học tập → Tải bảng điểm. Bảng điểm xuất dưới dạng PDF có chữ ký số và mã QR."),
    ("điểm cập nhật sau nộp bài", "Bài trắc nghiệm cập nhật điểm ngay lập tức. Bài tự luận cần 1-5 ngày làm việc tùy theo lịch chấm bài của giảng viên."),
    # Giảng Viên
    ("liên hệ với giảng viên", "Bạn có thể đặt câu hỏi trong phần Hỏi & Đáp (Q&A) của từng bài học, hoặc nhắn tin qua hệ thống tin nhắn nội bộ. Giảng viên thường phản hồi trong 24-48 giờ."),
    ("giảng viên trả lời câu hỏi bao lâu", "Giảng viên cam kết trả lời câu hỏi trong vòng 48 giờ làm việc."),
    ("xem hồ sơ giảng viên", "Nhấn vào tên giảng viên trên trang khóa học để xem hồ sơ đầy đủ gồm kinh nghiệm làm việc, bằng cấp, các khóa học đang giảng dạy."),
    ("đánh giá giảng viên", "Có! Sau khi hoàn thành khóa học, bạn có thể đánh giá sao (1-5) và viết nhận xét về chất lượng giảng dạy."),
    ("giảng viên không phản hồi", "Nếu chờ quá 72 giờ mà chưa có phản hồi, bạn gửi báo cáo qua Hỗ trợ. Đội ngũ quản lý sẽ liên hệ giảng viên."),
    # Lịch Học
    ("lịch học được sắp xếp như thế nào", "Nội dung được chia thành các tuần/chương có trình tự logic. Bạn có thể học theo thứ tự đề xuất hoặc nhảy qua lại tùy nhu cầu."),
    ("học theo tốc độ của riêng mình", "Có! Hầu hết khóa học là dạng tự học (self-paced) — bạn học khi nào, ở đâu và với tốc độ nào cũng được."),
    ("nhắc nhở lịch học tự động", "Có! Bạn có thể đặt mục tiêu học tập trong Cài đặt → Mục tiêu học tập. Hệ thống sẽ gửi nhắc nhở qua email."),
    ("bỏ lỡ buổi học trực tuyến xem lại được không", "Hầu hết buổi live session được ghi lại và đăng tải trong vòng 24 giờ sau khi kết thúc."),
    # Hủy Khóa Học
    ("hủy đăng ký khóa học", "Có thể yêu cầu hủy trong thời hạn quy định (thường 7 ngày từ ngày mua và chưa xem quá 30% nội dung)."),
    ("thời hạn hủy khóa học được hoàn tiền", "Bạn có 7 ngày kể từ ngày thanh toán để yêu cầu hủy và hoàn tiền đầy đủ, với điều kiện đã xem dưới 30% nội dung."),
    ("dữ liệu học tập sau khi hủy", "Nếu yêu cầu hoàn tiền được chấp thuận, quyền truy cập và dữ liệu học tập sẽ bị xóa."),
    ("đăng ký lại sau khi hủy", "Có! Bạn có thể đăng ký lại bất cứ lúc nào. Tuy nhiên, tiến trình học cũ sẽ không được khôi phục."),
    ("cách hủy khóa học", "Vào Tài khoản → Khóa học của tôi → chọn khóa muốn hủy → nhấn 'Yêu cầu hủy đăng ký' → điền lý do và xác nhận."),
    # Hoàn Tiền
    ("chính sách hoàn tiền", "Chúng tôi áp dụng chính sách hoàn tiền 100% trong vòng 7 ngày nếu bạn không hài lòng và đã xem dưới 30% nội dung."),
    ("gửi yêu cầu hoàn tiền", "Vào Hỗ trợ → Yêu cầu hoàn tiền, điền mã đơn hàng và lý do yêu cầu, đính kèm bằng chứng nếu có, rồi nhấn Gửi."),
    ("tiền hoàn trả về đâu bao lâu", "Tiền được hoàn về phương thức thanh toán ban đầu: thẻ ngân hàng trong 5-7 ngày, ví điện tử trong 1-3 ngày."),
    ("đã xem 50% khóa học có được hoàn tiền không", "Theo chính sách tiêu chuẩn, đã xem trên 30% nội dung sẽ không đủ điều kiện hoàn tiền. Liên hệ hỗ trợ để được xem xét."),
    ("đổi khóa học thay vì hoàn tiền", "Có! Thay vì hoàn tiền, bạn có thể yêu cầu chuyển sang khóa học khác có cùng hoặc thấp hơn giá trị."),
    # Hỗ Trợ Kỹ Thuật
    ("video bị giật lag", "Thử giảm chất lượng video xuống 480p, đóng bớt các tab trình duyệt, và đảm bảo kết nối internet ổn định (tối thiểu 5 Mbps)."),
    ("cấu hình máy tính tốc độ internet yêu cầu", "Yêu cầu tối thiểu: RAM 4GB, trình duyệt Chrome/Firefox phiên bản mới nhất, tốc độ internet 5 Mbps để xem video HD."),
    ("ứng dụng di động hỗ trợ hệ điều hành nào", "Ứng dụng hỗ trợ iOS 13.0 trở lên và Android 8.0 trở lên. Tải về miễn phí trên App Store và Google Play."),
    ("tải video bài giảng xem offline", "Có! Ứng dụng di động cho phép tải video để xem offline. Nhấn biểu tượng Tải xuống cạnh bài học."),
    ("phụ đề subtitle video", "Nhiều khóa học có phụ đề tiếng Việt và tiếng Anh. Nhấn biểu tượng CC trong trình phát video để bật/tắt phụ đề."),
    ("xóa cache cookie", "Trên Chrome: nhấn Ctrl+Shift+Delete → chọn Cache và Cookie → nhấn Xóa dữ liệu. Sau đó làm mới trang."),
    ("không nghe được âm thanh video", "Kiểm tra: âm lượng hệ thống, âm lượng trong trình phát video, cài đặt âm thanh trình duyệt. Thử tai nghe khác và làm mới trang."),
    ("liên hệ hỗ trợ kỹ thuật", "Liên hệ qua live chat trên website hoặc email hỗ trợ. Hỗ trợ viên phục vụ từ 8:00-22:00 mỗi ngày."),
    # Chatbot AI
    ("chatbot hỗ trợ được gì", "Chatbot có thể giúp bạn: tra cứu thông tin khóa học, hướng dẫn đăng ký, giải đáp câu hỏi thường gặp và theo dõi tiến trình học."),
    ("chatbot hoạt động 24/7 không", "Có! Chatbot AI hoạt động 24 giờ/7 ngày không nghỉ, sẵn sàng hỗ trợ bạn bất kỳ lúc nào."),
    ("chatbot hỗ trợ tiếng việt không", "Có! Chatbot được tối ưu hoàn toàn cho tiếng Việt, hiểu cả ngôn ngữ tự nhiên."),
    ("chatbot giúp tìm khóa học phù hợp", "Có! Cho chatbot biết lĩnh vực quan tâm, trình độ hiện tại và mục tiêu. Chatbot sẽ đề xuất khóa học phù hợp nhất."),
    # Chứng Chỉ
    ("cấp chứng chỉ khi nào", "Chứng chỉ được cấp sau khi bạn hoàn thành 100% khóa học và đạt điểm tối thiểu 70%. Vào Hồ sơ → Chứng chỉ để xem và tải về."),
    ("chứng chỉ có giá trị pháp lý không", "Chứng chỉ của chúng tôi là chứng nhận từ nền tảng, không tương đương bằng cấp nhà nước. Tuy nhiên, nhiều doanh nghiệp đối tác công nhận trong tuyển dụng."),
    ("tải chứng chỉ về máy", "Vào Hồ sơ → Chứng chỉ → chọn chứng chỉ cần tải → nhấn 'Tải xuống PDF'. Chứng chỉ có mã QR xác thực."),
    ("chia sẻ chứng chỉ lên linkedin", "Mỗi chứng chỉ có nút 'Chia sẻ lên LinkedIn' trực tiếp. Bạn cũng có thể copy link xác thực để đính kèm trong CV."),
    # Chính Sách
    ("chính sách bảo mật thông tin", "Thông tin của bạn được mã hóa SSL và lưu trữ theo tiêu chuẩn bảo mật. Chúng tôi không chia sẻ dữ liệu cho bên thứ ba."),
    ("chống đạo văn gian lận thi cử", "Hệ thống sử dụng phần mềm phát hiện đạo văn. Hành vi gian lận sẽ bị điểm 0 và có thể dẫn đến đình chỉ tài khoản."),
    ("chia sẻ tài khoản người khác", "Không! Tài khoản chỉ dành cho cá nhân đăng ký. Chia sẻ tài khoản vi phạm điều khoản và có thể bị khóa vĩnh viễn."),
    ("quy định ngôn ngữ diễn đàn", "Học viên cần sử dụng ngôn ngữ lịch sự, tôn trọng, không spam. Vi phạm sẽ bị xóa nội dung và cảnh cáo."),
]


def get_db_context():
    """Lấy dữ liệu THẬT từ database — tự động cập nhật mỗi lần gọi, không cache"""
    try:
        from apps.courses.models import Course, Category
        from apps.users.models import User
        from apps.exams.models import Exam
        from apps.assignments.models import Assignment
        from apps.enrollments.models import Enrollment

        categories = list(Category.objects.all().values('name', 'description'))

        courses = list(
            Course.objects.filter(status='published')
            .select_related('instructor', 'category')
            .values(
                'id', 'title', 'description', 'level', 'price',
                'duration_hours', 'instructor__full_name', 'category__name',
            )
        )

        exams = list(
            Exam.objects.filter(is_active=True)
            .select_related('course')
            .values('title', 'course__title', 'duration_minutes', 'pass_score', 'total_questions')
        )

        total_students = User.objects.filter(role='student').count()
        total_instructors = User.objects.filter(role='instructor').count()
        total_enrollments = Enrollment.objects.count()
        total_assignments = Assignment.objects.count()

        return {
            'categories': categories,
            'courses': courses,
            'exams': exams,
            'level_map': {
                'beginner': 'Cơ bản',
                'intermediate': 'Trung cấp',
                'advanced': 'Nâng cao',
            },
            'total_students': total_students,
            'total_instructors': total_instructors,
            'total_enrollments': total_enrollments,
            'total_assignments': total_assignments,
        }
    except Exception:
        return None


def normalize(text):
    text = text.lower().strip()
    text = re.sub(r'[?!.,;:\'"()\[\]{}]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def search_courses_in_db(q, words, db):
    """
    Tìm khóa học thật từ DB theo nhiều tiêu chí:
    - Tên khóa học (title)
    - Mô tả (description)
    - Danh mục (category)
    - Giảng viên (instructor)
    - Level (beginner/intermediate/advanced)
    """
    if not db or not db.get('courses'):
        return []

    level_map = db['level_map']
    level_reverse = {v.lower(): k for k, v in level_map.items()}
    # thêm từ khóa level thường gặp
    level_keywords = {
        'cơ bản': 'beginner', 'beginner': 'beginner', 'mới bắt đầu': 'beginner',
        'trung cấp': 'intermediate', 'intermediate': 'intermediate', 'trung bình': 'intermediate',
        'nâng cao': 'advanced', 'advanced': 'advanced', 'khó': 'advanced',
    }

    # Xác định level filter nếu có
    filter_level = None
    for kw, lv in level_keywords.items():
        if kw in q:
            filter_level = lv
            break

    matched = []
    for c in db['courses']:
        title_lower = (c['title'] or '').lower()
        desc_lower = (c.get('description') or '').lower()
        cat_lower = (c.get('category__name') or '').lower()
        inst_lower = (c.get('instructor__full_name') or '').lower()

        # Lọc theo level nếu user yêu cầu
        if filter_level and c.get('level') != filter_level:
            continue

        # Tính điểm match
        score = 0
        for word in words:
            if len(word) < 2:
                continue
            if word in title_lower:
                score += 3  # title quan trọng nhất
            if word in cat_lower:
                score += 2
            if word in desc_lower:
                score += 1
            if word in inst_lower:
                score += 1

        if score > 0:
            matched.append((score, c))

    # Sắp xếp theo điểm match giảm dần
    matched.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in matched]


def format_course(c, level_map):
    price_str = "Miễn phí" if not c['price'] or float(str(c['price'])) == 0 \
        else f"{int(float(str(c['price']))):,}đ"
    level_str = level_map.get(c.get('level', ''), c.get('level', ''))
    inst = c.get('instructor__full_name') or 'N/A'
    cat = c.get('category__name') or 'Chưa phân loại'
    hours = c.get('duration_hours', '')
    return f"📚 **{c['title']}** | {cat} | {level_str} | {price_str} | {hours}h | GV: {inst}"


def find_best_answer(question, db):
    q = normalize(question)
    words = set(q.split())

    level_map = db['level_map'] if db else {}

    # ══════════════════════════════════════════════════════
    # ƯU TIÊN 1: Hỏi về khóa học cụ thể → tìm trong DB TRƯỚC
    # ══════════════════════════════════════════════════════
    course_trigger_words = [
        'khóa học', 'khóa', 'học', 'môn', 'course', 'lớp', 'lớp học',
        'muốn học', 'tìm khóa', 'có khóa', 'dạy', 'giảng', 'tư vấn',
    ]
    is_course_query = any(kw in q for kw in course_trigger_words)

    if is_course_query and db:
        # Hỏi danh sách / liệt kê tất cả
        if any(w in q for w in ['tất cả', 'danh sách', 'liệt kê', 'xem', 'có gì', 'gồm có', 'bao gồm', 'hiện có']):
            courses = db['courses']
            if courses:
                lines = [format_course(c, level_map) for c in courses[:20]]
                more = f"\n_(và {len(courses) - 20} khóa học khác...)_" if len(courses) > 20 else ""
                return (
                    f"Hệ thống hiện có **{len(courses)} khóa học** đang mở:\n\n"
                    + "\n".join(lines) + more
                    + "\n\nBạn muốn tìm hiểu thêm về khóa nào? Tôi sẽ tư vấn chi tiết! 😊"
                )

        # Tìm kiếm theo từ khóa cụ thể
        matched_courses = search_courses_in_db(q, words, db)
        if matched_courses:
            lines = [format_course(c, level_map) for c in matched_courses[:8]]
            return (
                f"Tôi tìm thấy **{len(matched_courses)} khóa học** phù hợp với yêu cầu của bạn:\n\n"
                + "\n".join(lines)
                + ("\n_(và các khóa khác...)_" if len(matched_courses) > 8 else "")
                + "\n\nBạn muốn biết thêm về khóa học nào? 🎯"
            )

    # ══════════════════════════════════════════════════════
    # ƯU TIÊN 2: Hỏi về học phí / giá
    # ══════════════════════════════════════════════════════
    price_keywords = ['giá', 'học phí', 'tiền', 'miễn phí', 'phí', 'bao nhiêu tiền', 'bao nhiêu', 'chi phí']
    if any(kw in q for kw in price_keywords) and db and db.get('courses'):
        courses = db['courses']
        free = [c for c in courses if not c['price'] or float(str(c['price'])) == 0]
        paid = sorted(
            [c for c in courses if c['price'] and float(str(c['price'])) > 0],
            key=lambda x: float(str(x['price']))
        )
        result = f"💰 **Học phí các khóa học** (tổng {len(courses)} khóa):\n\n"
        if free:
            result += f"🆓 **Miễn phí** ({len(free)} khóa):\n"
            for c in free[:5]:
                result += f"  • {c['title']}\n"
            if len(free) > 5:
                result += f"  _(và {len(free)-5} khóa miễn phí khác)_\n"
        if paid:
            result += f"\n💳 **Có phí** ({len(paid)} khóa):\n"
            for c in paid[:5]:
                result += f"  • {c['title']}: {int(float(str(c['price']))):,}đ\n"
            if len(paid) > 5:
                result += f"  _(và {len(paid)-5} khóa có phí khác)_\n"
        return result + "\nVào trang **Khóa học** để xem đầy đủ và so sánh! 🎯"

    # ══════════════════════════════════════════════════════
    # ƯU TIÊN 3: Hỏi về danh mục / lĩnh vực
    # ══════════════════════════════════════════════════════
    category_keywords = ['danh mục', 'category', 'loại', 'ngành', 'chuyên ngành', 'lĩnh vực', 'mảng']
    if any(kw in q for kw in category_keywords) and db and db.get('categories'):
        cats = db['categories']
        cat_lines = [
            f"🏷️ **{c['name']}**" + (f": {c['description']}" if c.get('description') else "")
            for c in cats
        ]
        return (
            f"Hệ thống có **{len(cats)} danh mục** khóa học:\n\n"
            + "\n".join(cat_lines)
            + "\n\nBạn muốn xem khóa học trong danh mục nào? 📚"
        )

    # ══════════════════════════════════════════════════════
    # ƯU TIÊN 4: Hỏi về kỳ thi / đề thi
    # ══════════════════════════════════════════════════════
    exam_keywords = ['bài thi', 'đề thi', 'thi', 'kiểm tra', 'exam', 'ôn thi', 'ôn tập', 'kỳ thi']
    if any(kw in q for kw in exam_keywords) and db and db.get('exams'):
        exams = db['exams']
        matched = []
        for e in exams:
            title_lower = (e['title'] or '').lower()
            course_lower = (e.get('course__title') or '').lower()
            score = sum(
                3 if w in title_lower else (1 if w in course_lower else 0)
                for w in words if len(w) >= 2
            )
            if score > 0:
                matched.append((score, e))
        matched.sort(key=lambda x: x[0], reverse=True)
        show_list = [e for _, e in matched[:10]] if matched else exams[:10]
        lines = [
            f"📝 **{e['title']}** | Môn: {e['course__title']} "
            f"| {e['duration_minutes']} phút | {e['total_questions']} câu "
            f"| Điểm đạt: {e['pass_score']}%"
            for e in show_list
        ]
        label = f"tìm thấy **{len(matched)} kỳ thi** phù hợp" if matched else f"có **{len(exams)} kỳ thi** đang hoạt động"
        return (
            f"Hệ thống {label}:\n\n" + "\n".join(lines)
            + "\n\nBạn muốn ôn tập môn nào? Tôi sẽ tư vấn thêm! 📚"
        )

    # ══════════════════════════════════════════════════════
    # ƯU TIÊN 5: Hỏi thống kê hệ thống
    # ══════════════════════════════════════════════════════
    stats_keywords = ['tổng', 'bao nhiêu', 'có bao nhiêu', 'số lượng', 'thống kê', 'tổng quan']
    if any(kw in q for kw in stats_keywords) and db:
        return (
            f"📊 **Thống kê hệ thống Smart E-Learning:**\n\n"
            f"👩‍🎓 Sinh viên: **{db['total_students']}** người\n"
            f"👨‍🏫 Giảng viên: **{db['total_instructors']}** người\n"
            f"📚 Khóa học đang mở: **{len(db['courses'])}** khóa\n"
            f"🏷️ Danh mục: **{len(db['categories'])}** danh mục\n"
            f"📝 Kỳ thi: **{len(db['exams'])}** đề thi\n"
            f"📋 Bài tập: **{db['total_assignments']}** bài tập\n"
            f"🎓 Lượt đăng ký: **{db['total_enrollments']}** lượt\n\n"
            "Bạn muốn tìm hiểu thêm về khóa học nào không? 😊"
        )

    # ══════════════════════════════════════════════════════
    # ƯU TIÊN 6: FAQ tĩnh (hỏi về tính năng hệ thống, không liên quan DB)
    # ══════════════════════════════════════════════════════
    best_score = 0
    best_answer = None
    for keywords, answer in QA_LIST:
        kw_words = set(normalize(keywords).split())
        overlap = len(words & kw_words)
        if kw_words:
            score = overlap / len(kw_words)
            if overlap >= 1 and score > best_score:
                best_score = score
                best_answer = answer

    if best_answer and best_score >= 0.3:
        return best_answer

    return None


class AIChatView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        message = request.data.get('message', '').strip()
        if not message:
            return Response({'reply': 'Vui lòng nhập câu hỏi!'})

        # Lấy dữ liệu THẬT từ DB — luôn query mới, không cache
        # → Khi admin/giảng viên tạo khóa học mới, chatbot thấy ngay lập tức
        db = get_db_context()

        q = normalize(message)

        # Xử lý chào hỏi
        if any(w in q for w in ['xin chào', 'hello', 'hi ', 'chào', 'hey', 'alo', 'hi!', 'chao', 'xin chao']):
            cat_count = len(db['categories']) if db else 0
            course_count = len(db['courses']) if db else 0
            exam_count = len(db['exams']) if db else 0
            return Response({'reply': (
                f"Xin chào! 👋 Tôi là trợ lý của hệ thống **Smart E-Learning**.\n\n"
                f"Hệ thống hiện có **{course_count} khóa học** trong **{cat_count} danh mục** "
                f"và **{exam_count} kỳ thi** đang hoạt động.\n\n"
                "Tôi có thể giúp bạn:\n"
                "📚 Tìm khóa học theo tên, danh mục, trình độ\n"
                "💰 Tra cứu học phí, khóa học miễn phí\n"
                "📝 Tra cứu thông tin kỳ thi\n"
                "❓ Giải đáp thắc mắc về đăng ký, bài tập, chứng chỉ\n\n"
                "Bạn cần hỗ trợ gì? 😊"
            )})

        answer = find_best_answer(message, db)

        if answer:
            return Response({'reply': answer})

        return Response({'reply': (
            "Tôi chưa có thông tin về câu hỏi này. 🙏\n\n"
            "Bạn có thể thử:\n"
            "📚 Hỏi tên khóa học cụ thể (VD: 'có khóa Python không?')\n"
            "🏷️ Hỏi theo lĩnh vực (VD: 'khóa học lập trình', 'khóa tiếng Anh')\n"
            "💰 Hỏi về giá (VD: 'khóa học miễn phí', 'học phí bao nhiêu')\n"
            "📞 Hoặc liên hệ hỗ trợ trực tiếp qua live chat\n\n"
            "Thử hỏi lại nhé! 😊"
        )})
