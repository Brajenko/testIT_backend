# Generated by Django 5.0.6 on 2024-05-14 16:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('completions', '0002_completion_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='completion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='completions.completion'),
        ),
    ]