# Generated by Django 5.0.6 on 2024-05-25 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0016_remove_question_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='title',
        ),
        migrations.AddField(
            model_name='question',
            name='text',
            field=models.TextField(default='text of the question', max_length=150, verbose_name='text'),
            preserve_default=False,
        ),
    ]
