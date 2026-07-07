from django.core.management.base import BaseCommand
from apps.library.models import Book


class Command(BaseCommand):
    help = 'Thêm vài sách/tài liệu tham khảo miễn phí mẫu vào Thư viện (chỉ dùng link chính chủ, hợp pháp)'

    def handle(self, *args, **options):
        books = [
            {
                'title': 'Automate the Boring Stuff with Python',
                'author': 'Al Sweigart',
                'category': 'Lập trình',
                'description': 'Sách nhập môn Python miễn phí, tập trung tự động hóa các tác vụ văn phòng thường ngày. '
                                'Được tác giả cho phép đọc miễn phí trực tuyến theo giấy phép Creative Commons.',
                'cover_url': 'https://automatetheboringstuff.com/images/cover.png',
                'file_url': 'https://automatetheboringstuff.com/',
                'pages': 592,
            },
            {
                'title': 'Eloquent JavaScript',
                'author': 'Marijn Haverbeke',
                'category': 'Lập trình Web',
                'description': 'Sách nhập môn JavaScript hiện đại, từ cơ bản đến nâng cao. Tác giả phát hành miễn phí '
                                'trực tuyến trên trang chủ chính thức.',
                'cover_url': 'https://eloquentjavascript.net/img/cover.jpg',
                'file_url': 'https://eloquentjavascript.net/',
                'pages': 472,
            },
            {
                'title': 'Pro Git',
                'author': 'Scott Chacon & Ben Straub',
                'category': 'Công cụ phát triển',
                'description': 'Sách chính thức, đầy đủ nhất về Git — từ cơ bản đến các kỹ thuật nâng cao. '
                                'Miễn phí đọc trực tuyến trên trang chính thức của Git.',
                'cover_url': 'https://git-scm.com/images/progit2.png',
                'file_url': 'https://git-scm.com/book/en/v2',
                'pages': 456,
            },
            {
                'title': 'Think Python 2e',
                'author': 'Allen B. Downey',
                'category': 'Lập trình',
                'description': 'Giáo trình nhập môn lập trình bằng Python theo hướng tư duy khoa học máy tính, '
                                'phát hành miễn phí bởi Green Tea Press.',
                'cover_url': '',
                'file_url': 'https://greenteapress.com/thinkpython2/thinkpython2.pdf',
                'pages': 290,
            },
            {
                'title': 'Structure and Interpretation of Computer Programs',
                'author': 'Harold Abelson & Gerald Jay Sussman',
                'category': 'Khoa học máy tính',
                'description': 'Giáo trình kinh điển của MIT về các nguyên lý lập trình: đệ quy, trừu tượng hóa, '
                                'module hóa. MIT Press cho phép đọc miễn phí trực tuyến theo giấy phép CC BY-SA.',
                'cover_url': 'https://covers.openlibrary.org/b/isbn/9780262510875-L.jpg',
                'file_url': 'https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pres_0/6515/sicp.zip/full-text/book/book.html',
                'pages': 657,
            },
            {
                'title': "You Don't Know JS Yet",
                'author': 'Kyle Simpson',
                'category': 'Lập trình Web',
                'description': 'Bộ sách đi sâu vào bản chất của JavaScript: scope, closures, prototype, async... '
                                'Tác giả phát hành miễn phí trên GitHub chính thức.',
                'cover_url': '',
                'file_url': 'https://github.com/getify/You-Dont-Know-JS',
                'pages': 700,
            },
            {
                'title': 'The Rust Programming Language',
                'author': 'Steve Klabnik & Carol Nichols',
                'category': 'Lập trình',
                'description': 'Sách chính thức về ngôn ngữ Rust, do đội ngũ phát triển Rust biên soạn. '
                                'Bản HTML/PDF được phát hành miễn phí (Apache/MIT license) trên trang tài liệu chính thức.',
                'cover_url': 'https://covers.openlibrary.org/b/isbn/9781593278281-L.jpg',
                'file_url': 'https://doc.rust-lang.org/book/',
                'pages': 552,
            },
            {
                'title': 'The Linux Command Line',
                'author': 'William E. Shotts',
                'category': 'Hệ điều hành',
                'description': 'Giới thiệu toàn diện về dòng lệnh Linux, từ điều hướng file đến viết script Bash. '
                                'Phát hành miễn phí bởi tác giả trên LinuxCommand.org (giấy phép CC BY-NC-ND).',
                'cover_url': '',
                'file_url': 'https://linuxcommand.org/tlcl.php',
                'pages': 555,
            },
        ]

        created_count = 0
        for data in books:
            _, created = Book.objects.get_or_create(title=data['title'], defaults=data)
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Đã thêm {created_count} tài liệu mới vào Thư viện (tổng cộng {Book.objects.count()} tài liệu).'
        ))
