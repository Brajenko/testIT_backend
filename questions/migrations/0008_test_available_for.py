# Generated by Django 5.0.6 on 2024-05-13 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('questions', '0007_alter_variant_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='available_for',
            field=models.ManyToManyField(related_name='available_test', to='auth.group'),
        ),
    ]
