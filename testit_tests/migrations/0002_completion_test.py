# Generated by Django 5.0.1 on 2024-02-03 16:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testit_tests', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='completion',
            name='test',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='testit_tests.test'),
            preserve_default=False,
        ),
    ]