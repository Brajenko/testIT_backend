# Generated by Django 5.0.6 on 2024-05-17 18:38

import questions.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0012_auto_20240517_2138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='public_uuid',
            field=models.CharField(blank=True, default=questions.models.get_length_8_uuid, max_length=8, unique=True, verbose_name='public uuid'),
        ),
    ]
