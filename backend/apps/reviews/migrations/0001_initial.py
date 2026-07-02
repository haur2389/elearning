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
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('rating', models.PositiveIntegerField(default=5)),
                ('comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='courses.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='users.user')),
            ],
            options={'db_table': 'reviews', 'unique_together': {('course', 'student')}},
        ),
    ]
