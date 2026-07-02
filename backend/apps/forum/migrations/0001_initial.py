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
            name='ForumPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('is_pinned', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='forum_posts', to='courses.course')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='forum_posts', to='users.user')),
            ],
            options={'db_table': 'forum_posts', 'ordering': ['-is_pinned', '-created_at']},
        ),
        migrations.CreateModel(
            name='ForumReply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('is_solution', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='forum.forumpost')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='forum_replies', to='users.user')),
            ],
            options={'db_table': 'forum_replies', 'ordering': ['created_at']},
        ),
    ]
