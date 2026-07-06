# Thêm các loại thông báo mới: đề thi mới, có bài nộp mới, học viên vừa thi,
# đăng ký khóa học mới (chỉ đổi choices của notif_type, không đụng gì khác).
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notif_type',
            field=models.CharField(
                choices=[
                    ('new_lesson', 'Bài học mới'),
                    ('new_exam', 'Đề thi mới'),
                    ('new_assignment', 'Bài tập mới'),
                    ('new_submission', 'Có bài nộp mới'),
                    ('exam_attempt', 'Học viên vừa thi'),
                    ('assignment_graded', 'Đã chấm bài'),
                    ('exam_result', 'Kết quả thi'),
                    ('new_enrollment', 'Đăng ký khóa học mới'),
                    ('new_reply', 'Trả lời mới'),
                    ('system', 'Hệ thống'),
                ],
                default='system',
                max_length=30,
            ),
        ),
    ]
