from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='thumbnail',
            field=models.CharField(blank=True, help_text='URL ảnh hoặc đường dẫn file', max_length=500, null=True),
        ),
    ]
