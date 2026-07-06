from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('users', '0001_initial'),
        ('courses', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('duration_minutes', models.PositiveIntegerField(default=30)),
                ('total_questions', models.PositiveIntegerField(default=10)),
                ('pass_score', models.PositiveIntegerField(default=50)),
                ('is_random', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exams', to='courses.course')),
            ],
            options={'db_table': 'exams', 'verbose_name': 'Đề thi'},
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('question_type', models.CharField(choices=[('multiple_choice','Trắc nghiệm'),('true_false','Đúng/Sai'),('fill_blank','Điền khuyết'),('essay','Tự luận')], default='multiple_choice', max_length=20)),
                ('option_a', models.CharField(blank=True, max_length=500)),
                ('option_b', models.CharField(blank=True, max_length=500)),
                ('option_c', models.CharField(blank=True, max_length=500)),
                ('option_d', models.CharField(blank=True, max_length=500)),
                ('correct_answer', models.CharField(max_length=500)),
                ('points', models.PositiveIntegerField(default=1)),
                ('order', models.PositiveIntegerField(default=0)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='exams.exam')),
            ],
            options={'db_table': 'questions', 'ordering': ['order']},
        ),
        migrations.CreateModel(
            name='ExamResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('score', models.FloatField(default=0)),
                ('total_points', models.PositiveIntegerField(default=0)),
                ('earned_points', models.PositiveIntegerField(default=0)),
                ('is_passed', models.BooleanField(default=False)),
                ('answers', models.JSONField(default=dict)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('submitted_at', models.DateTimeField(null=True, blank=True)),
                ('time_spent', models.PositiveIntegerField(default=0)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_results', to='users.user')),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='exams.exam')),
            ],
            options={'db_table': 'exam_results'},
        ),
    ]
