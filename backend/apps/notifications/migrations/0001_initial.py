from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('users', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('notif_type', models.CharField(default='system', max_length=30)),
                ('is_read', models.BooleanField(default=False)),
                ('link', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='users.user')),
            ],
            options={'db_table': 'notifications', 'ordering': ['-created_at']},
        ),
    ]
