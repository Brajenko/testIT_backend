# Generated by Django 5.0.6 on 2024-06-04 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0018_checkbody_strict_score_question_points'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='text',
            field=models.TextField(verbose_name='text'),
        ),
    ]