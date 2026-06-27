import os
import json
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions


class AIChatView(APIView):
    permission_classes = [permissions.AllowAny]

    SYSTEM_PROMPT = """Bạn là AI trợ lý học tập thông minh của hệ thống Smart E-Learning - Đại học Bình Dương.

NHIỆM VỤ CHÍNH:
1. Trả lời câu hỏi dựa trên cơ sở dữ liệu Q&A bên dưới - ĐÂY LÀ NGUỒN THÔNG TIN CHÍNH XÁC NHẤT
2. Tư vấn đăng ký môn học, lộ trình học phù hợp
3. Hỗ trợ kỹ thuật lập trình: Python, Java, Web, SQL, AI/ML
4. Hướng dẫn sử dụng hệ thống

QUY TẮC TRẢ LỜI:
- Luôn trả lời bằng tiếng Việt, thân thiện
- Ưu tiên dùng thông tin từ cơ sở dữ liệu Q&A bên dưới
- Với câu hỏi kỹ thuật: đưa code mẫu kèm giải thích
- Dùng emoji và markdown cho dễ đọc
- Kết thúc bằng câu hỏi gợi mở

CƠ SỞ DỮ LIỆU CÂU HỎI & TRẢ LỜI (170 Q&A):

## Đăng Ký Tài Khoản
Q: Làm thế nào để đăng ký tài khoản mới trên hệ thống?
A: Bạn truy cập trang chủ, nhấn nút 'Đăng ký', điền đầy đủ thông tin họ tên, email, mật khẩu rồi nhấn 'Hoàn tất'. Hệ thống sẽ gửi email xác nhận để kích hoạt tài khoản.

Q: Tôi cần cung cấp những thông tin gì khi đăng ký tài khoản?
A: Bạn cần cung cấp: họ và tên, địa chỉ email hợp lệ, mật khẩu (tối thiểu 8 ký tự) và số điện thoại liên lạc. Một số trường hợp có thể yêu cầu xác minh danh tính.

Q: Tại sao tôi không nhận được email xác nhận đăng ký?
A: Email có thể nằm trong thư mục Spam/Rác. Vui lòng kiểm tra và đánh dấu là 'Không phải spam'. Nếu vẫn không thấy, hãy nhấn 'Gửi lại email xác nhận' hoặc liên hệ hỗ trợ.

Q: Tôi có thể đăng ký bằng tài khoản Google hoặc Facebook không?
A: Có! Hệ thống hỗ trợ đăng ký nhanh qua Google và Facebook. Chỉ cần nhấn nút tương ứng tại trang đăng ký và cấp quyền truy cập là xong.

Q: Tuổi tối thiểu để đăng ký tài khoản học trực tuyến là bao nhiêu?
A: Người dùng phải từ 13 tuổi trở lên để tự đăng ký. Học viên dưới 18 tuổi cần có sự đồng ý của phụ huynh hoặc người giám hộ theo quy định của hệ thống.

Q: Một người có thể tạo nhiều tài khoản không?
A: Mỗi người chỉ được tạo một tài khoản cá nhân. Việc tạo nhiều tài khoản vi phạm điều khoản sử dụng và có thể dẫn đến khóa tất cả các tài khoản liên quan.

Q: Làm thế nào để xác minh email sau khi đăng ký?
A: Sau khi đăng ký, hệ thống gửi email chứa nút 'Xác minh tài khoản'. Nhấn vào nút đó để hoàn tất. Link có hiệu lực trong 24 giờ kể từ khi nhận được email.

Q: Tôi bị lỗi 'Email đã tồn tại' khi đăng ký, phải làm gì?
A: Email này đã được dùng để đăng ký trước đó. Bạn thử chức năng 'Quên mật khẩu' để lấy lại quyền truy cập, hoặc dùng địa chỉ email khác để tạo tài khoản mới.

Q: Đăng ký tài khoản có mất phí không?
A: Hoàn toàn miễn phí! Việc tạo tài khoản không tốn bất kỳ chi phí nào. Phí chỉ phát sinh khi bạn đăng ký các khóa học có trả phí.

Q: Sau khi đăng ký, tôi có thể bắt đầu học ngay không?
A: Sau khi xác minh email thành công, bạn có thể đăng nhập và bắt đầu khám phá các khóa học miễn phí ngay lập tức. Khóa học trả phí cần hoàn tất thanh toán trước khi truy cập.


## Đăng Nhập
Q: Tôi không thể đăng nhập vào tài khoản, phải làm gì?
A: Vui lòng kiểm tra lại email và mật khẩu, đảm bảo không bật Caps Lock. Nếu quên mật khẩu, hãy dùng chức năng 'Quên mật khẩu'. Nếu vẫn không được, liên hệ bộ phận hỗ trợ.

Q: Tại sao tài khoản của tôi bị khóa sau nhiều lần đăng nhập sai?
A: Đây là biện pháp bảo mật tự động. Sau 5 lần nhập sai, tài khoản bị khóa tạm thời 30 phút. Bạn có thể đặt lại mật khẩu ngay để mở khóa sớm hơn.

Q: Tôi có thể đăng nhập trên nhiều thiết bị cùng lúc không?
A: Có, bạn có thể đăng nhập đồng thời trên tối đa 3 thiết bị. Nếu vượt quá giới hạn, phiên đăng nhập cũ nhất sẽ tự động bị đăng xuất.

Q: Làm thế nào để đăng nhập bằng tài khoản mạng xã hội?
A: Tại trang đăng nhập, nhấn nút 'Đăng nhập với Google' hoặc 'Đăng nhập với Facebook', sau đó cấp quyền truy cập. Tài khoản sẽ tự động liên kết với email tương ứng.

Q: Phiên đăng nhập của tôi sẽ hết hạn sau bao lâu?
A: Phiên đăng nhập thông thường hết hạn sau 7 ngày không hoạt động. Nếu bật 'Ghi nhớ đăng nhập', thời gian kéo dài lên 30 ngày.

Q: Tôi có thể bật tính năng 'Ghi nhớ đăng nhập' không?
A: Có! Tích vào ô 'Ghi nhớ đăng nhập' khi đăng nhập để hệ thống lưu phiên trong 30 ngày. Lưu ý không dùng tính năng này trên thiết bị công cộng.

Q: Làm thế nào để kích hoạt xác thực hai bước (2FA)?
A: Vào Cài đặt tài khoản → Bảo mật → Bật xác thực hai bước. Bạn có thể chọn nhận mã OTP qua SMS hoặc ứng dụng Google Authenticator.

Q: Sau khi đăng xuất, dữ liệu học tập của tôi có bị mất không?
A: Không bao giờ! Toàn bộ tiến trình học, điểm số và bài tập của bạn được lưu trữ an toàn trên máy chủ. Đăng nhập lại là bạn tiếp tục được ngay từ chỗ dừng.

Q: Tôi đăng nhập thành công nhưng không thấy khóa học đã mua, phải làm gì?
A: Hãy kiểm tra xem bạn đang đăng nhập đúng tài khoản dùng để mua không. Nếu đúng rồi, thử làm mới trang hoặc liên hệ hỗ trợ kèm mã đơn hàng để được xử lý ngay.

Q: Hệ thống có hỗ trợ đăng nhập SSO cho doanh nghiệp không?
A: Có! Hệ thống hỗ trợ Single Sign-On (SSO) cho tổ chức và doanh nghiệp thông qua SAML 2.0 và OAuth 2.0. Vui lòng liên hệ bộ phận kinh doanh để được tư vấn tích hợp.


## Quên Mật Khẩu
Q: Làm thế nào để lấy lại mật khẩu khi bị quên?
A: Tại trang đăng nhập, nhấn 'Quên mật khẩu', nhập email đăng ký và nhấn Gửi. Hệ thống sẽ gửi link đặt lại mật khẩu đến email của bạn trong vài phút.

Q: Tôi không nhận được email đặt lại mật khẩu, phải làm gì?
A: Kiểm tra thư mục Spam/Rác trước. Đảm bảo bạn nhập đúng email đăng ký. Nếu chờ quá 10 phút vẫn không thấy, hãy thử gửi lại hoặc liên hệ hỗ trợ.

Q: Link đặt lại mật khẩu có hiệu lực trong bao lâu?
A: Link đặt lại mật khẩu có hiệu lực trong 1 giờ kể từ khi gửi. Nếu hết hạn, bạn cần quay lại trang 'Quên mật khẩu' để yêu cầu gửi link mới.

Q: Tôi có thể đặt lại mật khẩu qua số điện thoại không?
A: Có! Nếu bạn đã liên kết số điện thoại với tài khoản, hệ thống có thể gửi mã OTP qua SMS để xác minh và đặt lại mật khẩu.

Q: Mật khẩu mới phải đáp ứng yêu cầu gì?
A: Mật khẩu cần tối thiểu 8 ký tự, bao gồm ít nhất 1 chữ hoa, 1 chữ thường, 1 số và 1 ký tự đặc biệt (@, #, $...). Không được trùng với 3 mật khẩu gần nhất.

Q: Tôi đã thay đổi mật khẩu nhưng vẫn không đăng nhập được?
A: Hãy thử xóa cache trình duyệt và thử lại. Đảm bảo bạn nhập mật khẩu mới vừa tạo, không phải mật khẩu cũ. Nếu vẫn lỗi, liên hệ hỗ trợ để kiểm tra tài khoản.

Q: Tôi quên cả email đăng ký, làm thế nào để khôi phục tài khoản?
A: Liên hệ bộ phận hỗ trợ qua live chat hoặc email, cung cấp họ tên, số điện thoại đăng ký và thông tin giao dịch. Đội ngũ sẽ xác minh và hỗ trợ khôi phục tài khoản.

Q: Sau bao nhiêu lần nhập sai mật khẩu thì tài khoản bị khóa?
A: Tài khoản bị khóa tạm thời sau 5 lần nhập sai mật khẩu liên tiếp. Bạn cần chờ 30 phút hoặc đặt lại mật khẩu ngay để mở khóa.

Q: Tôi có thể yêu cầu đặt lại mật khẩu bao nhiêu lần mỗi ngày?
A: Hệ thống giới hạn 5 lần yêu cầu đặt lại mật khẩu mỗi ngày để bảo vệ tài khoản. Nếu vượt giới hạn, vui lòng thử lại vào ngày hôm sau hoặc liên hệ hỗ trợ.

Q: Làm thế nào để thay đổi mật khẩu khi đang đăng nhập?
A: Vào Cài đặt tài khoản → Bảo mật → Đổi mật khẩu. Nhập mật khẩu hiện tại và mật khẩu mới hai lần rồi nhấn Lưu. Thay đổi có hiệu lực ngay lập tức.


## Hồ Sơ Cá Nhân
Q: Làm thế nào để cập nhật thông tin hồ sơ cá nhân?
A: Nhấn vào ảnh đại diện góc trên bên phải → Hồ sơ của tôi → Chỉnh sửa. Cập nhật thông tin cần thiết và nhấn Lưu thay đổi.

Q: Tôi có thể thay đổi tên hiển thị của mình không?
A: Có! Vào Hồ sơ cá nhân → Chỉnh sửa, thay đổi tên hiển thị và nhấn Lưu. Tên mới sẽ xuất hiện trong các bình luận và chứng chỉ hoàn thành khóa học.

Q: Làm thế nào để tải lên ảnh đại diện?
A: Vào Hồ sơ → Chỉnh sửa → nhấn vào vùng ảnh đại diện, chọn ảnh từ máy tính, cắt ảnh theo tỷ lệ mong muốn và nhấn Lưu.

Q: Ảnh đại diện cần đáp ứng yêu cầu kích thước và định dạng gì?
A: Ảnh cần có định dạng JPG, PNG hoặc GIF, kích thước tối thiểu 200x200px, tối đa 5MB. Hệ thống sẽ tự động cắt ảnh về tỷ lệ 1:1 (hình vuông).

Q: Tôi có thể thay đổi địa chỉ email đã đăng ký không?
A: Có, nhưng cần xác minh. Vào Cài đặt → Tài khoản → Đổi email, nhập email mới và xác minh qua link gửi đến email cũ. Email mới có hiệu lực sau khi xác nhận.

Q: Làm thế nào để thêm hoặc thay đổi số điện thoại liên lạc?
A: Vào Hồ sơ → Chỉnh sửa → điền số điện thoại mới → nhấn Lưu. Hệ thống sẽ gửi mã OTP để xác minh số điện thoại trước khi cập nhật.

Q: Thông tin cá nhân của tôi có được bảo mật không?
A: Hoàn toàn bảo mật! Thông tin của bạn được mã hóa SSL và lưu trữ theo tiêu chuẩn bảo mật quốc tế. Chúng tôi cam kết không chia sẻ dữ liệu cho bên thứ ba khi chưa có sự đồng ý.

Q: Tôi có thể xóa tài khoản và dữ liệu cá nhân không?
A: Có, bạn có quyền yêu cầu xóa tài khoản. Vào Cài đặt → Tài khoản → Xóa tài khoản và làm theo hướng dẫn. Lưu ý: hành động này không thể hoàn tác và toàn bộ dữ liệu sẽ bị xóa vĩnh viễn.

Q: Làm thế nào để xem lịch sử hoạt động học tập của mình?
A: Vào Hồ sơ → Lịch sử học tập để xem danh sách khóa học đã tham gia, tiến trình hoàn thành, điểm số và thời gian học tích lũy.

Q: Tôi có thể đặt hồ sơ ở chế độ riêng tư không?
A: Có! Vào Cài đặt → Quyền riêng tư, bạn có thể tùy chỉnh ai được xem hồ sơ, tiến trình học và danh sách khóa học của mình (Công khai / Chỉ mình tôi).


## Đăng Ký Khóa Học
Q: Làm thế nào để tìm kiếm và đăng ký khóa học?
A: Dùng thanh tìm kiếm hoặc duyệt qua danh mục để tìm khóa học. Nhấn vào khóa học, xem chi tiết rồi nhấn 'Đăng ký ngay' hoặc 'Mua khóa học' để hoàn tất.

Q: Tôi có thể xem trước nội dung khóa học trước khi đăng ký không?
A: Có! Mỗi khóa học đều có phần giới thiệu miễn phí gồm mô tả, mục tiêu, nội dung chương trình và 1-3 bài học mẫu để bạn trải nghiệm trước khi quyết định.

Q: Một tài khoản có thể đăng ký tối đa bao nhiêu khóa học cùng lúc?
A: Không giới hạn số lượng! Bạn có thể đăng ký và học song song nhiều khóa học tùy theo nhu cầu và khả năng tài chính của mình.

Q: Khóa học có giới hạn số lượng học viên không?
A: Hầu hết khóa học không giới hạn học viên. Tuy nhiên, một số lớp học trực tiếp hoặc có mentor kèm riêng sẽ có giới hạn chỗ. Thông tin này được hiển thị rõ trên trang khóa học.

Q: Tôi có thể tặng khóa học cho người khác không?
A: Có! Tại trang chi tiết khóa học, nhấn 'Tặng khóa học', nhập email người nhận và hoàn tất thanh toán. Người nhận sẽ nhận email thông báo và có thể kích hoạt khóa học của mình.

Q: Làm thế nào để đăng ký khóa học theo nhóm hoặc doanh nghiệp?
A: Liên hệ bộ phận kinh doanh qua email hoặc hotline để được tư vấn gói doanh nghiệp. Chúng tôi có ưu đãi đặc biệt cho đăng ký nhóm từ 10 người trở lên.

Q: Sau khi đăng ký, tôi có thể truy cập khóa học trong bao lâu?
A: Thời hạn truy cập phụ thuộc vào từng khóa học, thường là trọn đời (lifetime access). Thông tin cụ thể được ghi rõ tại trang chi tiết khóa học trước khi bạn đăng ký.

Q: Khóa học có yêu cầu kiến thức nền tảng gì không?
A: Mỗi khóa học đều ghi rõ yêu cầu kiến thức đầu vào trong phần mô tả. Bạn nên đọc kỹ phần này và thử bài học mẫu để đánh giá xem khóa học có phù hợp không.

Q: Tôi có thể đăng ký khóa học bằng mã giảm giá không? Nhập mã ở đâu?
A: Có! Tại trang thanh toán, bạn sẽ thấy ô 'Nhập mã giảm giá'. Điền mã và nhấn Áp dụng — hệ thống sẽ tự động tính toán và hiển thị số tiền được giảm.

Q: Làm thế nào để biết khóa học có phù hợp với trình độ của tôi không?
A: Xem phần 'Đối tượng phù hợp' và 'Yêu cầu đầu vào' trên trang khóa học. Bạn cũng có thể xem đánh giá từ học viên cùng trình độ hoặc hỏi chatbot để được tư vấn.


## Thanh Toán
Q: Hệ thống hỗ trợ những phương thức thanh toán nào?
A: Hệ thống hỗ trợ: thẻ tín dụng/ghi nợ (Visa, Mastercard), chuyển khoản ngân hàng, ví điện tử (MoMo, ZaloPay, VNPay) và thanh toán qua QR Code.

Q: Thanh toán trên hệ thống có an toàn không?
A: Hoàn toàn an toàn! Mọi giao dịch được mã hóa SSL 256-bit và xử lý qua cổng thanh toán đạt chuẩn PCI DSS. Chúng tôi không lưu trữ thông tin thẻ của bạn.

Q: Tôi có thể thanh toán bằng chuyển khoản ngân hàng không?
A: Có! Chọn phương thức 'Chuyển khoản ngân hàng' tại trang thanh toán, hệ thống sẽ cung cấp thông tin tài khoản và mã đơn hàng. Khóa học mở sau khi xác nhận giao dịch (1-2 giờ làm việc).

Q: Làm thế nào để áp dụng mã voucher khi thanh toán?
A: Tại trang thanh toán, nhập mã voucher vào ô 'Mã giảm giá' và nhấn Áp dụng. Số tiền giảm sẽ được trừ trực tiếp vào tổng thanh toán.

Q: Tôi thanh toán thành công nhưng chưa mở được khóa học?
A: Vui lòng chờ 5-15 phút và làm mới trang. Nếu vẫn chưa mở, liên hệ hỗ trợ kèm ảnh chụp xác nhận giao dịch để được xử lý ưu tiên trong vòng 1 giờ.

Q: Hóa đơn và biên lai thanh toán được gửi như thế nào?
A: Sau khi thanh toán thành công, hệ thống tự động gửi biên lai điện tử đến email đăng ký của bạn. Bạn cũng có thể xem và tải lại tại mục Lịch sử giao dịch trong tài khoản.

Q: Tôi có thể yêu cầu xuất hóa đơn VAT không?
A: Có! Tại trang thanh toán, tích vào ô 'Yêu cầu hóa đơn VAT' và điền thông tin doanh nghiệp (mã số thuế, địa chỉ). Hóa đơn sẽ được xuất và gửi trong vòng 3-5 ngày làm việc.

Q: Thanh toán trả góp có được hỗ trợ không?
A: Có! Hệ thống hỗ trợ trả góp 0% lãi suất qua thẻ tín dụng của các ngân hàng liên kết (3, 6, 12 tháng). Tùy chọn này sẽ hiển thị tại trang thanh toán nếu khóa học đủ điều kiện.

Q: Tôi có thể hủy giao dịch sau khi đã thanh toán không?
A: Giao dịch đã hoàn tất không thể hủy trực tiếp. Tuy nhiên, bạn có thể yêu cầu hoàn tiền theo chính sách hoàn tiền trong vòng 7 ngày nếu đáp ứng điều kiện.

Q: Thời gian xử lý thanh toán là bao lâu?
A: Thanh toán qua ví điện tử và thẻ ngân hàng xử lý tức thì. Chuyển khoản ngân hàng cần 1-2 giờ làm việc. Trả góp qua thẻ có thể mất 15-30 phút để xác nhận.


## Học Phí
Q: Học phí các khóa học được tính như thế nào?
A: Học phí được định giá theo từng khóa học dựa trên độ dài, chất lượng nội dung và kinh nghiệm giảng viên. Giá được hiển thị rõ ràng trên trang chi tiết mỗi khóa học.

Q: Có gói học phí theo tháng hoặc năm không?
A: Có! Hệ thống cung cấp gói Subscription cho phép học không giới hạn khóa học trong kho với mức phí cố định theo tháng hoặc năm, tiết kiệm hơn nhiều so với mua từng khóa.

Q: Học viên mới có được ưu đãi học phí không?
A: Có! Học viên đăng ký lần đầu được giảm 20-30% cho khóa học đầu tiên. Ưu đãi này áp dụng tự động khi thanh toán hoặc qua mã chào mừng gửi trong email xác nhận tài khoản.

Q: Có chính sách giảm học phí cho sinh viên hoặc người có thu nhập thấp không?
A: Có! Chúng tôi có chương trình học bổng và giảm giá đặc biệt cho sinh viên (cần xác minh thẻ sinh viên) và người có hoàn cảnh khó khăn. Liên hệ hỗ trợ để biết thêm chi tiết.

Q: Học phí có thể thay đổi sau khi tôi đã đăng ký không?
A: Không! Học phí bị khóa tại thời điểm bạn mua. Dù giá khóa học tăng sau đó, bạn vẫn được truy cập đầy đủ với mức giá đã thanh toán.

Q: Tôi có thể so sánh học phí giữa các gói học không?
A: Có! Trang Bảng giá của hệ thống hiển thị bảng so sánh chi tiết giữa gói Free, Cơ bản và Premium, giúp bạn dễ dàng chọn gói phù hợp nhất.

Q: Hệ thống có hỗ trợ học bổng không?
A: Có! Chúng tôi có quỹ học bổng hàng quý cho học viên xuất sắc và hoàn cảnh khó khăn. Thông tin và đơn đăng ký học bổng được công bố trên trang Học bổng trong hệ thống.

Q: Học phí đã bao gồm thuế VAT chưa?
A: Giá hiển thị trên trang khóa học đã bao gồm VAT. Khi thanh toán, bạn sẽ thấy bảng chi tiết phân tách giá gốc và thuế để minh bạch hoàn toàn.

Q: Tôi cần đóng học phí bổ sung nếu khóa học được cập nhật thêm nội dung không?
A: Không! Bạn chỉ trả một lần và nhận quyền truy cập tất cả nội dung cập nhật trong tương lai của khóa học đó mà không phát sinh thêm chi phí.

Q: Làm thế nào để xem lịch sử các khoản thanh toán học phí?
A: Vào Tài khoản → Lịch sử giao dịch để xem toàn bộ các khoản thanh toán, ngày thực hiện, phương thức và trạng thái. Bạn cũng có thể tải biên lai PDF cho từng giao dịch.


## Bài Kiểm Tra
Q: Bài kiểm tra trong khóa học có dạng như thế nào?
A: Bài kiểm tra có nhiều dạng: trắc nghiệm đơn/đa lựa chọn, điền vào chỗ trống, kéo thả và câu hỏi tự luận ngắn. Dạng cụ thể phụ thuộc vào từng khóa học và giảng viên thiết kế.

Q: Tôi có bao nhiêu lần làm lại bài kiểm tra nếu không đạt?
A: Số lần làm lại tùy quy định của từng khóa học, thường từ 2-3 lần. Sau mỗi lần làm, hệ thống sẽ hiển thị phần bạn cần ôn lại trước khi thử tiếp.

Q: Thời gian làm bài kiểm tra là bao lâu?
A: Thời gian làm bài được quy định riêng cho từng bài kiểm tra, thường từ 15-60 phút. Đồng hồ đếm ngược sẽ hiển thị rõ ràng góc trên màn hình trong suốt quá trình làm bài.

Q: Điểm tối thiểu để qua bài kiểm tra là bao nhiêu?
A: Điểm qua thường là 70% (7/10 điểm), nhưng có thể khác tùy khóa học. Yêu cầu điểm tối thiểu được thông báo rõ ràng trước khi bạn bắt đầu làm bài.

Q: Tôi có thể xem lại đáp án sau khi nộp bài không?
A: Tùy cài đặt của giảng viên. Một số bài kiểm tra cho xem đáp án ngay sau khi nộp, số khác chỉ hiển thị điểm số và phần trăm đúng để tránh chia sẻ đáp án.

Q: Bài kiểm tra có được giám sát trực tuyến không?
A: Một số bài kiểm tra quan trọng (thi chứng chỉ) có tính năng giám sát qua webcam và chống sao chép. Bạn sẽ được thông báo trước nếu bài thi có yêu cầu giám sát.

Q: Tôi bị mất kết nối internet giữa chừng khi làm bài, phải làm gì?
A: Đừng lo! Hệ thống tự động lưu câu trả lời mỗi 30 giây. Khi kết nối lại, bạn có thể tiếp tục từ câu đã trả lời. Thời gian mất kết nối vẫn được tính vào giới hạn thời gian.

Q: Kết quả bài kiểm tra có được lưu tự động không?
A: Có, toàn bộ kết quả được lưu tự động và hiển thị trong mục Kết quả kiểm tra của khóa học. Bạn có thể xem lại lịch sử tất cả các lần làm bài bất kỳ lúc nào.

Q: Tôi có thể làm bài kiểm tra trên điện thoại di động không?
A: Có! Giao diện bài kiểm tra được tối ưu cho cả máy tính và điện thoại. Tuy nhiên, với bài thi có giám sát webcam, nên sử dụng máy tính để đảm bảo chất lượng tốt nhất.

Q: Sau bao lâu thì kết quả bài kiểm tra được công bố?
A: Bài trắc nghiệm chấm điểm và trả kết quả ngay lập tức sau khi nộp. Bài tự luận có thể cần 1-3 ngày làm việc để giảng viên chấm và phản hồi.


## Bài Tập
Q: Bài tập trong khóa học có được chấm điểm tự động không?
A: Bài tập trắc nghiệm và lập trình được chấm tự động ngay sau khi nộp. Bài tập tự luận, đồ án và thiết kế cần giảng viên hoặc trợ giảng chấm thủ công.

Q: Làm thế nào để nộp bài tập trên hệ thống?
A: Vào bài học tương ứng → Bài tập → Làm bài. Điền câu trả lời hoặc tải file lên, kiểm tra lại và nhấn 'Nộp bài'. Hệ thống sẽ xác nhận nộp thành công qua thông báo.

Q: Bài tập có thời hạn nộp không?
A: Có! Mỗi bài tập đều hiển thị thời hạn nộp (deadline) rõ ràng. Hệ thống gửi nhắc nhở trước deadline 24 giờ và 1 giờ qua email và thông báo trong ứng dụng.

Q: Tôi có thể nộp bài tập trễ hạn không? Có bị trừ điểm không?
A: Tùy quy định từng khóa. Một số khóa cho phép nộp trễ với mức trừ điểm 10-30% mỗi ngày. Một số khóa không nhận bài sau deadline. Kiểm tra quy định trong phần mô tả bài tập.

Q: Định dạng file nộp bài tập được chấp nhận là gì?
A: Hệ thống chấp nhận: PDF, DOCX, XLSX, PPTX, JPG, PNG, MP4 và file nén ZIP/RAR. Định dạng cụ thể yêu cầu được ghi rõ trong đề bài tập.

Q: Kích thước file tối đa khi nộp bài tập là bao nhiêu?
A: File thông thường tối đa 50MB. File video tối đa 500MB. Nếu file vượt quá giới hạn, bạn có thể nén lại hoặc liên hệ giảng viên để được hỗ trợ cách nộp thay thế.

Q: Tôi có thể chỉnh sửa và nộp lại bài tập không?
A: Trước deadline, bạn có thể nộp lại nhiều lần — hệ thống ghi nhận lần nộp cuối cùng. Sau deadline, việc nộp lại phụ thuộc vào quyết định của giảng viên.

Q: Giảng viên có nhận xét về bài tập của tôi không?
A: Có! Giảng viên thường cung cấp nhận xét chi tiết trong vòng 3-5 ngày làm việc sau deadline. Bạn nhận thông báo qua email khi có phản hồi mới.

Q: Làm thế nào để xem bài tập mẫu hoặc hướng dẫn?
A: Trong phần mô tả bài tập, giảng viên thường đính kèm file hướng dẫn và bài mẫu tham khảo. Bạn cũng có thể đặt câu hỏi trong phần Thảo luận của bài học.

Q: Bài tập nhóm được thực hiện như thế nào trên hệ thống?
A: Giảng viên sẽ chia nhóm hoặc cho phép tự chọn nhóm qua hệ thống. Trưởng nhóm nộp bài thay mặt cả nhóm, điểm số được phân bổ đồng đều cho tất cả thành viên.


## Điểm Số
Q: Làm thế nào để xem điểm số tổng kết của khóa học?
A: Vào trang khóa học → Tiến trình học tập → Điểm số. Tại đây hiển thị điểm từng bài tập, kiểm tra và điểm tổng kết theo thang điểm 10.

Q: Điểm số được tính như thế nào (trọng số bài kiểm tra, bài tập)?
A: Công thức tính điểm được công bố trong phần Thông tin khóa học. Thường: bài tập chiếm 40%, kiểm tra giữa kỳ 20%, kiểm tra cuối kỳ 40%. Có thể khác theo từng khóa.

Q: Điểm bao nhiêu thì được cấp chứng chỉ hoàn thành?
A: Cần đạt tối thiểu 70% (7/10 điểm) và hoàn thành ít nhất 80% nội dung khóa học để được cấp chứng chỉ. Một số khóa chuyên sâu yêu cầu điểm cao hơn.

Q: Tôi có thể phúc khảo điểm nếu không đồng ý không?
A: Có! Trong vòng 7 ngày sau khi điểm được công bố, bạn có thể gửi yêu cầu phúc khảo qua mục Hỗ trợ, kèm lý do cụ thể. Giảng viên sẽ xem xét và phản hồi trong 5 ngày làm việc.

Q: Điểm số có bị xóa nếu tôi hủy khóa học không?
A: Nếu hủy trong thời hạn hoàn tiền và được xử lý, lịch sử điểm có thể bị xóa. Nếu chỉ ngừng học (không yêu cầu hoàn tiền), điểm vẫn được lưu trong lịch sử tài khoản.

Q: Làm thế nào để tải bảng điểm về máy?
A: Vào Hồ sơ → Thành tích học tập → Tải bảng điểm. Bảng điểm xuất dưới dạng PDF có chữ ký số và mã QR để xác minh tính hợp lệ.

Q: Điểm số có được cập nhật ngay sau khi nộp bài không?
A: Bài trắc nghiệm cập nhật điểm ngay lập tức. Bài tự luận cần 1-5 ngày làm việc tùy theo lịch chấm bài của giảng viên. Bạn nhận thông báo khi điểm được cập nhật.

Q: Tôi bị điểm 0 do nộp bài trễ, có thể khiếu nại không?
A: Có thể, nếu có lý do chính đáng (sự cố kỹ thuật, bệnh...). Gửi yêu cầu qua Hỗ trợ kèm bằng chứng trong vòng 48 giờ sau khi nhận kết quả. Giảng viên sẽ xem xét từng trường hợp.

Q: Hệ thống có bảng xếp hạng học viên theo điểm số không?
A: Có! Mỗi khóa học có bảng xếp hạng top 10 học viên đạt điểm cao nhất. Tính năng này khuyến khích tinh thần học tập, nhưng bạn có thể ẩn tên mình nếu muốn.

Q: Điểm số trong hệ thống có được công nhận bởi các tổ chức bên ngoài không?
A: Chứng chỉ của chúng tôi được một số tổ chức và doanh nghiệp đối tác công nhận. Danh sách đối tác được công bố trên trang Chứng chỉ & Đối tác. Bạn cũng có thể liên hệ hỗ trợ để xác nhận.


## Giảng Viên
Q: Làm thế nào để liên hệ với giảng viên của khóa học?
A: Bạn có thể đặt câu hỏi trực tiếp trong phần Hỏi & Đáp (Q&A) của từng bài học, hoặc nhắn tin qua hệ thống tin nhắn nội bộ. Giảng viên thường phản hồi trong 24-48 giờ.

Q: Giảng viên có trả lời câu hỏi của học viên không? Trong bao lâu?
A: Có! Giảng viên cam kết trả lời câu hỏi trong phần Q&A trong vòng 48 giờ làm việc. Câu hỏi phổ biến sẽ được ghim lên đầu để tất cả học viên cùng tham khảo.

Q: Tôi có thể đặt câu hỏi trực tiếp với giảng viên không?
A: Có thể qua phần Q&A của từng bài học hoặc diễn đàn thảo luận của khóa. Một số giảng viên cũng mở Office Hours (giờ hỗ trợ trực tiếp) định kỳ qua video call.

Q: Giảng viên có tổ chức buổi học trực tiếp (live session) không?
A: Tùy từng khóa học! Một số khóa có buổi live session định kỳ qua Zoom/Meet để giải đáp thắc mắc và thảo luận chuyên sâu. Lịch live session được thông báo trước trên trang khóa học.

Q: Làm thế nào để xem hồ sơ và kinh nghiệm của giảng viên?
A: Nhấn vào tên giảng viên trên trang khóa học để xem hồ sơ đầy đủ gồm kinh nghiệm làm việc, bằng cấp, các khóa học đang giảng dạy và đánh giá từ học viên.

Q: Tôi có thể đánh giá và phản hồi về giảng viên không?
A: Có! Sau khi hoàn thành khóa học, bạn có thể đánh giá sao (1-5) và viết nhận xét về chất lượng giảng dạy. Phản hồi giúp giảng viên cải thiện và giúp học viên khác lựa chọn.

Q: Nếu giảng viên không phản hồi, tôi phải liên hệ với ai?
A: Nếu chờ quá 72 giờ mà chưa có phản hồi, bạn gửi báo cáo qua Hỗ trợ. Đội ngũ quản lý sẽ liên hệ giảng viên và đảm bảo câu hỏi của bạn được giải đáp kịp thời.

Q: Giảng viên có cập nhật nội dung khóa học thường xuyên không?
A: Hầu hết giảng viên cam kết cập nhật nội dung ít nhất mỗi 6 tháng để đảm bảo kiến thức luôn mới nhất. Thông tin cập nhật gần nhất được ghi rõ trên trang khóa học.

Q: Một khóa học có thể có nhiều giảng viên không?
A: Có! Một số khóa học mời nhiều chuyên gia cùng giảng dạy các chuyên đề khác nhau. Danh sách tất cả giảng viên và phần họ phụ trách được liệt kê đầy đủ trên trang khóa học.

Q: Làm thế nào để theo dõi (follow) giảng viên yêu thích?
A: Vào trang hồ sơ giảng viên và nhấn nút 'Theo dõi'. Bạn sẽ nhận thông báo khi giảng viên mở khóa học mới, đăng thông báo hoặc tổ chức sự kiện.


## Lịch Học
Q: Lịch học của khóa học được sắp xếp như thế nào?
A: Nội dung được chia thành các tuần/chương có trình tự logic. Bạn có thể học theo thứ tự đề xuất hoặc nhảy qua lại tùy nhu cầu (với khóa học tự học).

Q: Tôi có thể học theo tốc độ của riêng mình không?
A: Có! Hầu hết khóa học là dạng tự học (self-paced) — bạn học khi nào, ở đâu và với tốc độ nào cũng được. Chỉ khóa học trực tiếp (live class) mới có lịch học cố định.

Q: Hệ thống có nhắc nhở lịch học tự động không?
A: Có! Bạn có thể đặt mục tiêu học tập trong Cài đặt → Mục tiêu học tập. Hệ thống sẽ gửi nhắc nhở qua email và thông báo đẩy (push notification) theo lịch bạn chọn.

Q: Làm thế nào để xem lịch học và lịch thi tổng hợp?
A: Vào mục Lịch học ở menu chính để xem toàn bộ lịch học, deadline bài tập và lịch thi của tất cả các khóa học đang tham gia dưới dạng lịch tháng/tuần.

Q: Tôi có thể tùy chỉnh thời gian học trong ngày không?
A: Hoàn toàn! Với khóa tự học, bạn truy cập 24/7. Hệ thống cũng cho phép đặt khung giờ học ưa thích để nhận nhắc nhở đúng lúc bạn muốn.

Q: Nếu bỏ lỡ một buổi học trực tuyến, tôi có thể xem lại không?
A: Hầu hết buổi live session được ghi lại và đăng tải trong vòng 24 giờ sau khi kết thúc. Bạn có thể xem lại toàn bộ bất kỳ lúc nào trong thời gian còn truy cập khóa học.

Q: Khóa học có kế hoạch học tập theo tuần không?
A: Nhiều khóa học cung cấp lộ trình học đề xuất theo tuần trong phần Tổng quan. Bạn có thể theo sát lộ trình này hoặc tự điều chỉnh phù hợp với thời gian của mình.

Q: Tôi có thể đồng bộ lịch học với Google Calendar không?
A: Có! Vào Cài đặt → Tích hợp lịch → Kết nối Google Calendar. Toàn bộ deadline, lịch thi và live session sẽ tự động xuất hiện trong Google Calendar của bạn.

Q: Lịch học có thay đổi khi giảng viên nghỉ không?
A: Nếu giảng viên nghỉ hoặc dời lịch live session, hệ thống sẽ thông báo đến tất cả học viên qua email và thông báo trong ứng dụng ít nhất 24 giờ trước.

Q: Làm thế nào để đặt nhắc nhở cho từng bài học cụ thể?
A: Vào bài học → nhấn biểu tượng chuông → Đặt nhắc nhở, chọn thời gian và hình thức (email/thông báo đẩy). Nhắc nhở sẽ gửi đúng giờ bạn đã hẹn.


## Hủy Khóa Học
Q: Tôi có thể hủy đăng ký khóa học không?
A: Có thể yêu cầu hủy trong thời hạn quy định (thường 7 ngày từ ngày mua và chưa xem quá 30% nội dung). Ngoài thời hạn này, việc hủy không đi kèm hoàn tiền.

Q: Thời hạn để hủy khóa học và được hoàn tiền là bao lâu?
A: Bạn có 7 ngày kể từ ngày thanh toán để yêu cầu hủy và hoàn tiền đầy đủ, với điều kiện đã xem dưới 30% nội dung. Xem thêm tại trang Chính sách hoàn tiền.

Q: Khi hủy khóa học, dữ liệu học tập của tôi có bị xóa không?
A: Nếu yêu cầu hoàn tiền được chấp thuận, quyền truy cập và dữ liệu học tập sẽ bị xóa. Nếu chỉ hủy mà không hoàn tiền (khóa đã hết hạn), dữ liệu có thể được giữ lại.

Q: Sau khi hủy, tôi có thể đăng ký lại khóa học đó không?
A: Có! Bạn có thể đăng ký lại bất cứ lúc nào. Tuy nhiên, tiến trình học cũ sẽ không được khôi phục — bạn cần bắt đầu lại từ đầu.

Q: Hủy khóa học có ảnh hưởng đến chứng chỉ đã nhận không?
A: Nếu đã nhận chứng chỉ trước khi hủy/hoàn tiền, chứng chỉ sẽ bị thu hồi và mã xác minh sẽ không còn hợp lệ. Chứng chỉ chỉ hợp lệ với tài khoản đang có quyền truy cập khóa học.

Q: Làm thế nào để hủy khóa học trên hệ thống?
A: Vào Tài khoản → Khóa học của tôi → chọn khóa muốn hủy → nhấn 'Yêu cầu hủy đăng ký' → điền lý do và xác nhận. Yêu cầu sẽ được xử lý trong 1-3 ngày làm việc.

Q: Tôi hủy khóa học do lỗi hệ thống, có được ưu tiên xử lý không?
A: Có! Nếu hủy do lỗi hệ thống, hãy liên hệ hỗ trợ ngay kèm ảnh chụp màn hình lỗi. Trường hợp này được xử lý ưu tiên và hoàn tiền 100% bất kể điều kiện thông thường.

Q: Khóa học theo gói (bundle) có thể hủy từng khóa riêng lẻ không?
A: Thông thường, gói bundle chỉ được hủy toàn bộ, không thể hủy từng khóa riêng lẻ. Tuy nhiên, một số gói có thể linh hoạt hơn — vui lòng liên hệ hỗ trợ để được tư vấn cụ thể.

Q: Tôi bị tính phí sau khi đã yêu cầu hủy, phải làm gì?
A: Liên hệ hỗ trợ ngay với thông tin yêu cầu hủy (ngày gửi, mã yêu cầu) và sao kê giao dịch bị tính phí sai. Đội ngũ sẽ xử lý và hoàn tiền trong vòng 5-7 ngày làm việc.

Q: Thông báo hủy khóa học có được gửi qua email không?
A: Có! Sau khi yêu cầu hủy được xử lý, hệ thống gửi email xác nhận đến địa chỉ đăng ký của bạn, bao gồm thông tin về trạng thái hoàn tiền (nếu có).


## Hoàn Tiền
Q: Chính sách hoàn tiền của hệ thống là gì?
A: Chúng tôi áp dụng chính sách hoàn tiền 100% trong vòng 7 ngày nếu bạn không hài lòng và đã xem dưới 30% nội dung. Xem đầy đủ tại trang Chính sách hoàn tiền.

Q: Trong bao nhiêu ngày sau khi mua tôi có thể yêu cầu hoàn tiền?
A: Trong vòng 7 ngày kể từ ngày thanh toán. Sau thời hạn này, yêu cầu hoàn tiền chỉ được xem xét trong trường hợp ngoại lệ như lỗi hệ thống hoặc nội dung sai mô tả.

Q: Làm thế nào để gửi yêu cầu hoàn tiền?
A: Vào Hỗ trợ → Yêu cầu hoàn tiền, điền mã đơn hàng và lý do yêu cầu, đính kèm bằng chứng nếu có, rồi nhấn Gửi. Bạn nhận email xác nhận tiếp nhận yêu cầu ngay lập tức.

Q: Tiền hoàn trả sẽ được trả về đâu và trong bao lâu?
A: Tiền được hoàn về phương thức thanh toán ban đầu: thẻ ngân hàng trong 5-7 ngày làm việc, ví điện tử trong 1-3 ngày, chuyển khoản trong 3-5 ngày tùy ngân hàng.

Q: Tôi đã hoàn thành 50% khóa học, có được hoàn tiền không?
A: Theo chính sách tiêu chuẩn, đã xem trên 30% nội dung sẽ không đủ điều kiện hoàn tiền. Tuy nhiên, nếu có lý do đặc biệt, hãy liên hệ hỗ trợ để được xem xét từng trường hợp.

Q: Mã giảm giá có được hoàn lại không khi hủy khóa học?
A: Mã giảm giá đã sử dụng không được hoàn lại dưới dạng mã giảm giá. Số tiền hoàn trả là số tiền thực tế bạn đã thanh toán sau khi áp dụng mã giảm giá.

Q: Hoàn tiền có áp dụng cho các khóa học khuyến mãi không?
A: Có, chính sách hoàn tiền áp dụng cho mọi khóa học kể cả đang khuyến mãi, miễn là đáp ứng điều kiện (trong 7 ngày, xem dưới 30% nội dung).

Q: Tôi có thể yêu cầu hoàn tiền nhiều lần không?
A: Hệ thống giới hạn 3 lần hoàn tiền trên cùng một tài khoản. Tài khoản có dấu hiệu lạm dụng chính sách hoàn tiền có thể bị hạn chế quyền mua khóa học.

Q: Nếu yêu cầu hoàn tiền bị từ chối, tôi có thể khiếu nại ở đâu?
A: Bạn có thể gửi khiếu nại qua email cấp cao hoặc yêu cầu xem xét lại qua mục Khiếu nại trong Hỗ trợ. Đội ngũ quản lý sẽ phản hồi trong vòng 3 ngày làm việc.

Q: Hệ thống có cho phép đổi khóa học thay vì hoàn tiền không?
A: Có! Thay vì hoàn tiền, bạn có thể yêu cầu chuyển sang khóa học khác có cùng hoặc thấp hơn giá trị. Tùy chọn này cho phép bạn tiếp tục học mà không mất phí.


## Hỗ Trợ Kỹ Thuật
Q: Video bài giảng bị giật, lag khi học, phải làm gì?
A: Hãy thử giảm chất lượng video xuống 480p hoặc 360p, đóng bớt các tab trình duyệt, và đảm bảo kết nối internet ổn định (tối thiểu 5 Mbps). Xóa cache trình duyệt cũng có thể giúp cải thiện.

Q: Hệ thống yêu cầu cấu hình máy tính và tốc độ internet tối thiểu là gì?
A: Yêu cầu tối thiểu: RAM 4GB, trình duyệt Chrome/Firefox phiên bản mới nhất, tốc độ internet 5 Mbps để xem video HD. Khóa có bài thực hành lập trình có thể yêu cầu cấu hình cao hơn.

Q: Ứng dụng di động hỗ trợ hệ điều hành nào?
A: Ứng dụng hỗ trợ iOS 13.0 trở lên và Android 8.0 (Oreo) trở lên. Tải về miễn phí trên App Store và Google Play. Phiên bản web cũng hoạt động tốt trên trình duyệt di động.

Q: Tôi có thể tải video bài giảng về xem offline không?
A: Có! Ứng dụng di động cho phép tải video để xem offline. Nhấn biểu tượng Tải xuống cạnh bài học. Tính năng này chỉ khả dụng trên app, không hỗ trợ trên trình duyệt web.

Q: Phụ đề (subtitle) có sẵn cho các video bài giảng không?
A: Nhiều khóa học có phụ đề tiếng Việt và tiếng Anh. Nhấn biểu tượng CC trong trình phát video để bật/tắt phụ đề và chọn ngôn ngữ. Hệ thống cũng hỗ trợ phụ đề tự động AI.

Q: Tôi gặp lỗi khi nộp bài tập, phải báo cáo ở đâu?
A: Nhấn vào nút Báo cáo lỗi ngay trong trang nộp bài, hoặc liên hệ Hỗ trợ kỹ thuật kèm ảnh chụp màn hình lỗi. Lỗi kỹ thuật được xử lý trong vòng 2-4 giờ làm việc.

Q: Làm thế nào để xóa cache và cookie khi gặp lỗi hiển thị?
A: Trên Chrome: nhấn Ctrl+Shift+Delete → chọn Cache và Cookie → nhấn Xóa dữ liệu. Sau đó làm mới trang. Thao tác này thường khắc phục hầu hết lỗi hiển thị thông thường.

Q: Hệ thống có hỗ trợ trình duyệt nào tốt nhất?
A: Google Chrome phiên bản mới nhất cho trải nghiệm tốt nhất. Mozilla Firefox và Microsoft Edge cũng được hỗ trợ đầy đủ. Không khuyến nghị dùng Internet Explorer vì không còn được hỗ trợ.

Q: Tôi không nghe được âm thanh trong video, phải kiểm tra gì?
A: Kiểm tra theo thứ tự: âm lượng hệ thống, âm lượng trong trình phát video, cài đặt âm thanh trình duyệt (biểu tượng loa cạnh tab). Thử tai nghe khác và làm mới trang nếu vẫn lỗi.

Q: Làm thế nào để liên hệ bộ phận hỗ trợ kỹ thuật 24/7?
A: Liên hệ qua: Live chat trên website (phản hồi trong 5 phút), email support@hoctructuyen.vn, hotline 1800-xxxx (miễn phí). Chatbot AI hoạt động 24/7, hỗ trợ viên trực từ 8:00-22:00 mỗi ngày.


## Chatbot AI
Q: Chatbot AI trên hệ thống có thể hỗ trợ tôi những gì?
A: Chatbot có thể giúp bạn: tra cứu thông tin khóa học, hướng dẫn đăng ký và thanh toán, giải đáp câu hỏi thường gặp, theo dõi tiến trình học và chuyển kết nối đến hỗ trợ viên khi cần.

Q: Chatbot có hoạt động 24/7 không?
A: Có! Chatbot AI hoạt động 24 giờ/7 ngày không nghỉ, sẵn sàng hỗ trợ bạn bất kỳ lúc nào. Với các yêu cầu phức tạp cần hỗ trợ viên, chatbot sẽ đặt lịch hẹn để được hỗ trợ trong giờ làm việc.

Q: Chatbot có thể trả lời câu hỏi về nội dung bài học không?
A: Chatbot có thể giải đáp các câu hỏi kiến thức cơ bản về nội dung bài học. Với câu hỏi chuyên sâu, chatbot sẽ hướng dẫn bạn đặt câu hỏi trong phần Q&A để giảng viên giải đáp trực tiếp.

Q: Làm thế nào để bắt đầu cuộc trò chuyện với chatbot?
A: Nhấn vào biểu tượng chat (bong bóng hội thoại) ở góc dưới bên phải màn hình, hoặc nhấn nút Hỗ trợ ở thanh điều hướng. Chatbot sẽ chào và hỏi bạn cần hỗ trợ gì.

Q: Nếu chatbot không hiểu câu hỏi của tôi, phải làm gì?
A: Thử diễn đạt lại câu hỏi theo cách khác đơn giản hơn, hoặc chọn chủ đề từ menu gợi ý của chatbot. Nếu vẫn không được, nhấn 'Kết nối hỗ trợ viên' để được hỗ trợ trực tiếp.

Q: Chatbot có lưu lịch sử cuộc trò chuyện không?
A: Có, lịch sử chat được lưu 30 ngày trong tài khoản của bạn. Bạn có thể xem lại bằng cách cuộn lên đầu cửa sổ chat hoặc vào Tài khoản → Lịch sử hỗ trợ.

Q: Tôi có thể chuyển từ chatbot sang hỗ trợ viên thực không?
A: Có! Nhấn nút 'Nói chuyện với hỗ trợ viên' hoặc nhập 'Kết nối nhân viên hỗ trợ'. Trong giờ làm việc (8:00-22:00), bạn sẽ được kết nối với hỗ trợ viên trong vài phút.

Q: Chatbot có hỗ trợ tiếng Việt không?
A: Có! Chatbot được tối ưu hoàn toàn cho tiếng Việt, hiểu cả ngôn ngữ tự nhiên và tiếng lóng thông dụng. Bạn cũng có thể chuyển sang tiếng Anh bằng cách gõ 'Switch to English'.

Q: Chatbot có thể giúp tôi tìm khóa học phù hợp không?
A: Có! Cho chatbot biết lĩnh vực quan tâm, trình độ hiện tại và mục tiêu của bạn. Chatbot sẽ phân tích và đề xuất 3-5 khóa học phù hợp nhất kèm lý do và so sánh chi tiết.

Q: Dữ liệu cuộc trò chuyện với chatbot có được bảo mật không?
A: Hoàn toàn bảo mật! Mọi cuộc trò chuyện được mã hóa end-to-end. Dữ liệu chỉ dùng để cải thiện chất lượng dịch vụ theo chính sách bảo mật đã được công bố và đồng ý.


## Chính Sách và Quy Định
Q: Chính sách bảo mật thông tin cá nhân của hệ thống là gì?
A: Chúng tôi thu thập và xử lý dữ liệu cá nhân theo quy định pháp luật Việt Nam và GDPR. Thông tin của bạn được mã hóa, không bán cho bên thứ ba và chỉ dùng để cải thiện trải nghiệm học tập.

Q: Điều khoản sử dụng dịch vụ có những nội dung quan trọng nào?
A: Các điểm quan trọng gồm: một người một tài khoản, không chia sẻ tài liệu có bản quyền, không gian lận trong bài kiểm tra, và tuân thủ quy tắc ứng xử trong cộng đồng học tập.

Q: Hệ thống có chính sách chống đạo văn và gian lận thi cử không?
A: Có! Hệ thống sử dụng phần mềm phát hiện đạo văn và giám sát bài thi. Hành vi gian lận sẽ bị điểm 0 cho bài đó và có thể dẫn đến đình chỉ tài khoản tùy mức độ vi phạm.

Q: Tài khoản vi phạm quy định sẽ bị xử lý như thế nào?
A: Tùy mức độ vi phạm: cảnh cáo (lần 1), hạn chế tính năng (lần 2) hoặc khóa tài khoản vĩnh viễn (vi phạm nghiêm trọng). Học viên có quyền khiếu nại nếu cho rằng bị xử lý oan.

Q: Tôi có thể chia sẻ tài khoản với người khác không?
A: Không! Tài khoản chỉ dành cho cá nhân đăng ký. Chia sẻ tài khoản vi phạm điều khoản sử dụng và có thể dẫn đến khóa tài khoản vĩnh viễn mà không được hoàn tiền.

Q: Nội dung khóa học có được bảo vệ bản quyền không?
A: Có! Toàn bộ nội dung (video, tài liệu, bài tập) thuộc bản quyền của giảng viên và nền tảng. Việc sao chép, phân phối hoặc tải về trái phép có thể bị xử lý theo pháp luật.

Q: Chứng chỉ hoàn thành khóa học có giá trị pháp lý không?
A: Chứng chỉ của chúng tôi là chứng nhận từ nền tảng, không tương đương bằng cấp nhà nước. Tuy nhiên, nhiều doanh nghiệp đối tác công nhận giá trị thực tế của chứng chỉ trong tuyển dụng.

Q: Hệ thống có quy định về ngôn ngữ và hành vi trong diễn đàn không?
A: Có! Học viên cần sử dụng ngôn ngữ lịch sự, tôn trọng, không phân biệt đối xử, không spam và không chia sẻ thông tin cá nhân người khác. Vi phạm sẽ bị xóa nội dung và cảnh cáo.

Q: Tôi có thể khiếu nại vi phạm quyền lợi học viên ở đâu?
A: Gửi khiếu nại qua email khieunai@hoctructuyen.vn hoặc mục Khiếu nại trong Hỗ trợ. Mọi khiếu nại được xem xét trong 5 ngày làm việc và giải quyết công bằng, minh bạch.

Q: Chính sách thu thập và sử dụng dữ liệu học tập là gì?
A: Dữ liệu học tập (tiến trình, điểm số, thời gian học) được thu thập để cá nhân hóa trải nghiệm học tập và cải thiện nội dung. Dữ liệu được ẩn danh hóa trước khi dùng cho nghiên cứu và không bao giờ bán cho bên thứ ba.

"""

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
            except Exception:
                pass

        # Thử Gemini API
        gemini_key = os.environ.get('GEMINI_API_KEY', '')
        if gemini_key:
            try:
                reply = self._call_gemini(message, history, gemini_key)
                if reply:
                    return Response({'reply': reply})
            except Exception:
                pass

        # Thử OpenAI API
        openai_key = os.environ.get('OPENAI_API_KEY', '')
        if openai_key:
            try:
                reply = self._call_openai(message, history, openai_key)
                if reply:
                    return Response({'reply': reply})
            except Exception:
                pass

        # Smart fallback
        reply = self._smart_reply(message)
        return Response({'reply': reply})

    def _call_claude(self, message, history, api_key):
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
            return response.json()['content'][0]['text']
        return None

    def _call_gemini(self, message, history, api_key):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=self.SYSTEM_PROMPT)
        chat_history = []
        for h in history[-8:]:
            role = 'user' if h.get('role') == 'user' else 'model'
            chat_history.append({'role': role, 'parts': [h.get('content', '')]})
        chat = model.start_chat(history=chat_history)
        return chat.send_message(message).text

    def _call_openai(self, message, history, api_key):
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
        m = msg.lower()

        # Chào hỏi
        if any(w in m for w in ['xin chào', 'hello', 'hi ', 'chào', 'hey', 'alo']):
            return ("Xin chào! 👋 Tôi là AI tư vấn học tập của **Smart E-Learning**.\n\n"
                    "Tôi có thể giúp bạn:\n"
                    "📚 **Tư vấn chọn khóa học** phù hợp với mục tiêu của bạn\n"
                    "🗺️ **Lộ trình học** từ cơ bản đến nâng cao\n"
                    "❓ **Giải đáp** thắc mắc về các môn học CNTT\n"
                    "🔧 **Hướng dẫn** sử dụng hệ thống học tập\n\n"
                    "Bạn đang muốn học gì hoặc cần tư vấn gì? 😊")

        # Đăng ký / tư vấn khóa học
        if any(w in m for w in ['đăng ký', 'chọn khóa', 'nên học', 'bắt đầu', 'lộ trình', 'học gì', 'tư vấn', 'muốn học']):
            return ("Tôi rất vui được tư vấn cho bạn! 🎯\n\n"
                    "Để tư vấn chính xác, cho tôi biết thêm một chút:\n\n"
                    "1️⃣ **Trình độ hiện tại** của bạn là gì?\n"
                    "   - 🌱 Chưa biết gì về lập trình\n"
                    "   - 📘 Đã biết cơ bản (HTML/Python...)\n"
                    "   - 💡 Đã có kinh nghiệm, muốn nâng cao\n\n"
                    "2️⃣ **Mục tiêu** bạn muốn đạt được?\n"
                    "   - 💼 Làm lập trình viên Web\n"
                    "   - 🤖 Làm AI/Data Science\n"
                    "   - 📱 Làm app Mobile\n"
                    "   - 🔒 Làm bảo mật/network\n"
                    "   - 🎓 Học để tốt nghiệp/thi\n\n"
                    "Bạn đang ở đâu và muốn đi đến đâu? Kể cho tôi nghe nhé! 😊")

        # Hướng dẫn cách đăng ký
        if any(w in m for w in ['cách đăng ký', 'làm sao đăng ký', 'đăng ký như thế nào', 'mua', 'enroll']):
            return ("📋 **Hướng dẫn đăng ký khóa học** (chỉ 3 bước!):\n\n"
                    "**Bước 1: Tạo tài khoản sinh viên**\n"
                    "→ Bấm **[Đăng ký]** ở góc trên phải trang chủ\n"
                    "→ Nhập email, mật khẩu, tên → Xác nhận email\n\n"
                    "**Bước 2: Tìm khóa học phù hợp**\n"
                    "→ Bấm **[Khóa học]** trên thanh menu\n"
                    "→ Lọc theo Danh mục, Trình độ (Cơ bản/Trung cấp/Nâng cao)\n"
                    "→ Bấm vào khóa học để xem chi tiết chương trình\n\n"
                    "**Bước 3: Đăng ký và bắt đầu học**\n"
                    "→ Bấm **[Đăng ký học ngay]** (nếu miễn phí → tức thì!)\n"
                    "→ Bấm **[Vào học]** để bắt đầu xem bài giảng\n\n"
                    "💡 **Lưu ý:** Chỉ tài khoản **sinh viên** mới được đăng ký học. Admin và Giảng viên dùng để quản lý.\n\n"
                    "Bạn đã có tài khoản chưa? Cần tôi tư vấn chọn khóa học nào không? 😊")

        # Lộ trình học Web
        if any(w in m for w in ['web', 'frontend', 'backend', 'fullstack', 'html', 'react', 'node']):
            return ("🌐 **Lộ trình học Lập trình Web:**\n\n"
                    "**Giai đoạn 1 - Nền tảng (2-3 tháng):**\n"
                    "✅ HTML/CSS → Xây dựng giao diện tĩnh\n"
                    "✅ JavaScript cơ bản → Tương tác với người dùng\n\n"
                    "**Giai đoạn 2 - Frontend (2-3 tháng):**\n"
                    "🔵 JavaScript nâng cao (ES6+, DOM, API)\n"
                    "🔵 React.js hoặc Vue.js\n"
                    "🔵 Git & GitHub\n\n"
                    "**Giai đoạn 3 - Backend (2-3 tháng):**\n"
                    "🟡 Node.js + Express hoặc Python/Django\n"
                    "🟡 Cơ sở dữ liệu SQL (MySQL/PostgreSQL)\n"
                    "🟡 RESTful API\n\n"
                    "**Giai đoạn 4 - Fullstack + Deploy:**\n"
                    "🟠 Kết hợp Frontend + Backend\n"
                    "🟠 Docker, Cloud (AWS/Vercel)\n\n"
                    "📚 **Trên E-Learning có các khóa:** HTML/CSS, JavaScript, React, Node.js, SQL\n\n"
                    "Bạn đang ở giai đoạn nào? Tôi sẽ gợi ý khóa học cụ thể! 🎯")

        # Lộ trình AI/ML
        if any(w in m for w in ['ai', 'machine learning', 'data science', 'deep learning', 'học máy', 'trí tuệ nhân tạo']):
            return ("🤖 **Lộ trình học AI/Data Science:**\n\n"
                    "**Bước 1 - Nền tảng (bắt buộc):**\n"
                    "✅ Python cơ bản → ngôn ngữ chính của AI\n"
                    "✅ Toán cho ML: Đại số tuyến tính, Xác suất thống kê\n"
                    "✅ NumPy, Pandas → xử lý dữ liệu\n\n"
                    "**Bước 2 - Machine Learning:**\n"
                    "🔵 Scikit-learn → các thuật toán cơ bản\n"
                    "🔵 Linear Regression, Decision Tree, SVM\n"
                    "🔵 Đánh giá mô hình (accuracy, F1-score)\n\n"
                    "**Bước 3 - Deep Learning:**\n"
                    "🟡 TensorFlow hoặc PyTorch\n"
                    "🟡 Neural Networks, CNN, RNN\n"
                    "🟡 Computer Vision / NLP\n\n"
                    "**Bước 4 - Chuyên sâu:**\n"
                    "🟠 Large Language Models (LLM)\n"
                    "🟠 Deployment với FastAPI, Docker\n\n"
                    "⏱ Thời gian ước tính: **12-18 tháng** học đầy đủ\n\n"
                    "Bạn đã biết Python chưa? Đó là điều kiện tiên quyết! 💡")

        # Python
        if any(w in m for w in ['python']):
            return ("🐍 **Python - Ngôn ngữ lý tưởng cho người mới:**\n\n"
                    "```python\n# Ví dụ Python cơ bản\nten = input('Bạn tên gì? ')\ntuoi = int(input('Bao nhiêu tuổi? '))\nprint(f'Chào {ten}! Bạn {tuoi} tuổi.')\n\n# Hàm đơn giản\ndef tinh_bmi(can_nang, chieu_cao):\n    bmi = can_nang / (chieu_cao ** 2)\n    return round(bmi, 2)\n\nprint(tinh_bmi(60, 1.7))  # 20.76\n```\n\n"
                    "**Tại sao nên học Python?**\n"
                    "✅ Cú pháp đơn giản, dễ đọc như tiếng Anh\n"
                    "✅ Dùng cho AI/ML, Web (Django), Data Science\n"
                    "✅ Cộng đồng lớn, nhiều thư viện\n"
                    "✅ Lương cao, nhiều việc làm\n\n"
                    "**Lộ trình Python:** Cơ bản → OOP → Thư viện (NumPy/Pandas) → Chuyên ngành\n\n"
                    "Bạn muốn dùng Python cho mục đích gì? Tôi sẽ tư vấn cụ thể hơn! 🎯")

        # SQL / CSDL
        if any(w in m for w in ['sql', 'cơ sở dữ liệu', 'csdl', 'database', 'mysql']):
            return ("🗄️ **SQL - Ngôn ngữ quản lý dữ liệu:**\n\n"
                    "```sql\n-- Tạo bảng sinh viên\nCREATE TABLE sinh_vien (\n    id INT PRIMARY KEY AUTO_INCREMENT,\n    ho_ten VARCHAR(100) NOT NULL,\n    email VARCHAR(100) UNIQUE,\n    khoa VARCHAR(50)\n);\n\n-- Thêm dữ liệu\nINSERT INTO sinh_vien (ho_ten, email, khoa)\nVALUES ('Nguyễn Văn A', 'a@ubd.edu.vn', 'CNTT');\n\n-- Truy vấn\nSELECT * FROM sinh_vien\nWHERE khoa = 'CNTT'\nORDER BY ho_ten ASC;\n```\n\n"
                    "**SQL cần thiết cho ai?**\n"
                    "✅ Lập trình viên Backend (bắt buộc)\n"
                    "✅ Data Analyst / Data Engineer\n"
                    "✅ DevOps, System Admin\n\n"
                    "Bạn đang học SQL để làm gì? Tôi sẽ gợi ý phần nào cần học trước! 💡")

        # Hỏi về bài tập, bài thi
        if any(w in m for w in ['bài tập', 'nộp bài', 'deadline', 'bài thi', 'thi', 'điểm', 'kết quả']):
            return ("📋 **Hướng dẫn về Bài tập & Bài thi:**\n\n"
                    "**📝 Xem & Nộp bài tập:**\n"
                    "1. Vào khóa học đã đăng ký → tab **[📋 Bài tập]**\n"
                    "2. Xem mô tả yêu cầu và hạn nộp\n"
                    "3. Bấm **[📤 Nộp bài]** → chọn file → upload\n"
                    "4. Chú ý deadline! Nộp muộn sẽ được đánh dấu 'Trễ hạn'\n\n"
                    "**📝 Làm bài thi:**\n"
                    "1. Vào khóa học → tab **[📝 Bài thi]**\n"
                    "2. Bấm **[✏️ Làm bài]** → đọc kỹ đề\n"
                    "3. Chú ý thời gian đếm ngược!\n"
                    "4. Bấm **[Nộp bài]** khi hoàn thành\n"
                    "5. Xem kết quả tức thì trong **[Kết quả thi]**\n\n"
                    "**⚠️ Lưu ý:** Chỉ sinh viên đã **đăng ký khóa học** mới được làm bài tập và bài thi.\n\n"
                    "Bạn có vấn đề cụ thể nào cần giải quyết không? 🤔")

        # Hỏi về tài khoản
        if any(w in m for w in ['tài khoản', 'đăng nhập', 'mật khẩu', 'account', 'login', 'register']):
            return ("🔐 **Quản lý tài khoản trên E-Learning:**\n\n"
                    "**Đăng ký tài khoản mới:**\n"
                    "→ Trang chủ → **[Đăng ký]** → Nhập thông tin → Xác nhận\n"
                    "→ Chọn role: **Sinh viên** (để học), Giảng viên (để dạy)\n\n"
                    "**Đăng nhập:**\n"
                    "→ Bấm **[Đăng nhập]** → Email + Mật khẩu\n\n"
                    "**Quên mật khẩu:**\n"
                    "→ Trang đăng nhập → **[Quên mật khẩu?]** → Nhập email\n\n"
                    "**Cập nhật hồ sơ:**\n"
                    "→ Click avatar góc phải → **[Hồ sơ cá nhân]**\n\n"
                    "❓ Bạn gặp vấn đề gì với tài khoản? Tôi có thể hướng dẫn chi tiết hơn!")

        # Câu hỏi chung
        return (f"Cảm ơn câu hỏi của bạn! 🤔\n\n"
                f"Bạn đang hỏi về: **{msg[:80]}**\n\n"
                "⚠️ *Chatbot đang chạy ở chế độ offline (chưa cấu hình API key AI). Để có câu trả lời thông minh hơn, admin cần cài đặt ANTHROPIC_API_KEY hoặc GEMINI_API_KEY.*\n\n"
                "Tôi có thể giúp bạn tốt nhất về:\n"
                "🎯 **Tư vấn chọn khóa học** - Hỏi: 'Tôi nên học gì?'\n"
                "🗺️ **Lộ trình học** - Hỏi: 'Lộ trình học Web/AI/Mobile?'\n"
                "📋 **Hướng dẫn hệ thống** - Hỏi: 'Cách đăng ký khóa học?'\n"
                "💻 **Kỹ thuật lập trình** - Python, SQL, Web...\n\n"
                "Hãy hỏi cụ thể hơn để tôi hỗ trợ bạn tốt nhất! 💪")
