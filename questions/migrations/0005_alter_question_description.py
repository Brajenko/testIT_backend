# Generated by Django 5.0.6 on 2024-05-11 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0004_question_type_alter_question_test_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='description'),
        ),
    ]
