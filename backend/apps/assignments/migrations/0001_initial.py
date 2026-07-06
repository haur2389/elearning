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
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('deadline', models.DateTimeField()),
                ('max_score', models.PositiveIntegerField(default=100)),
                ('attachment', models.FileField(blank=True, null=True, upload_to='assignments/files/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='courses.course')),
            ],
            options={'db_table': 'assignments'},
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('file', models.FileField(upload_to='submissions/')),
                ('note', models.TextField(blank=True)),
                ('score', models.FloatField(blank=True, null=True)),
                ('feedback', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('submitted','Đã nộp'),('graded','Đã chấm'),('late','Nộp muộn')], default='submitted', max_length=20)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('graded_at', models.DateTimeField(blank=True, null=True)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='assignments.assignment')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='users.user')),
            ],
            options={'db_table': 'submissions', 'unique_together': {('assignment', 'student')}},
        ),
    ]
