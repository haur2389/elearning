import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('enrollments', '0001_initial'),
        ('users', '0001_initial'),
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('method', models.CharField(
                    choices=[
                        ('momo', 'MoMo'),
                        ('vnpay', 'VNPay'),
                        ('zalopay', 'ZaloPay'),
                        ('bank_transfer', 'Chuyển khoản ngân hàng'),
                        ('free', 'Miễn phí'),
                    ],
                    default='free', max_length=20
                )),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Chờ thanh toán'),
                        ('completed', 'Thành công'),
                        ('failed', 'Thất bại'),
                        ('refunded', 'Đã hoàn tiền'),
                    ],
                    default='pending', max_length=20
                )),
                ('transaction_id', models.CharField(blank=True, max_length=100)),
                ('note', models.TextField(blank=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='payments',
                    to='users.user'
                )),
                ('course', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='payments',
                    to='courses.course'
                )),
            ],
            options={'db_table': 'payments', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('certificate_code', models.CharField(default=uuid.uuid4, max_length=50, unique=True)),
                ('issued_at', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='certificates',
                    to='users.user'
                )),
                ('course', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='certificates',
                    to='courses.course'
                )),
            ],
            options={
                'db_table': 'certificates',
                'ordering': ['-issued_at'],
                'unique_together': {('student', 'course')},
            },
        ),
    ]
