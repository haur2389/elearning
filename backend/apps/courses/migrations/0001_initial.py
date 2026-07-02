from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('users', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(blank=True, max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'db_table': 'categories', 'verbose_name': 'Danh mục'},
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('description', models.TextField()),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='courses/thumbnails/')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('level', models.CharField(choices=[('beginner','Cơ bản'),('intermediate','Trung cấp'),('advanced','Nâng cao')], default='beginner', max_length=20)),
                ('status', models.CharField(choices=[('draft','Bản nháp'),('published','Đã xuất bản'),('archived','Lưu trữ')], default='draft', max_length=20)),
                ('duration_hours', models.PositiveIntegerField(default=0)),
                ('requirements', models.TextField(blank=True)),
                ('objectives', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('instructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='users.user')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='courses', to='courses.category')),
            ],
            options={'db_table': 'courses', 'verbose_name': 'Khóa học', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chapters', to='courses.course')),
            ],
            options={'db_table': 'chapters', 'verbose_name': 'Chương', 'ordering': ['order']},
        ),
    ]
