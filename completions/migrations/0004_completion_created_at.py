# Generated by Django 5.0.6 on 2024-06-04 13:12

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('completions', '0003_alter_answer_completion'),
    ]

    operations = [
        migrations.AddField(
            model_name='completion',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
