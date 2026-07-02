from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('courses', '0001_initial'),
        ('users', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('content_type', models.CharField(choices=[('video','Video'),('pdf','PDF'),('text','Văn bản'),('slide','Slide')], default='video', max_length=20)),
                ('video_url', models.URLField(blank=True)),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='lessons/pdfs/')),
                ('slide_url', models.URLField(blank=True)),
                ('content', models.TextField(blank=True)),
                ('duration', models.PositiveIntegerField(default=0)),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_preview', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('chapter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='courses.chapter')),
            ],
            options={'db_table': 'lessons', 'verbose_name': 'Bài học', 'ordering': ['order']},
        ),
        migrations.CreateModel(
            name='LessonProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('watch_percentage', models.PositiveIntegerField(default=0)),
                ('is_completed', models.BooleanField(default=False)),
                ('last_watched', models.DateTimeField(auto_now=True)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress', to='lessons.lesson')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lesson_progress', to='users.user')),
            ],
            options={'db_table': 'lesson_progress', 'unique_together': {('student', 'lesson')}},
        ),
    ]
