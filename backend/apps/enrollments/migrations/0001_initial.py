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
            name='Enrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('progress', models.PositiveIntegerField(default=0)),
                ('is_completed', models.BooleanField(default=False)),
                ('enrolled_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(null=True, blank=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='users.user')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='courses.course')),
            ],
            options={'db_table': 'enrollments', 'unique_together': {('student', 'course')}},
        ),
    ]
