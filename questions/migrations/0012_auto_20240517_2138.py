# Generated by Django 5.0.6 on 2024-05-17 18:28

from questions.models import get_length_8_uuid
import questions.models
from django.db import migrations, models

def gen_uuid(apps, schema_editor):
    Test = apps.get_model("questions", "Test")
    for row in Test.objects.all():
        row.public_uuid = get_length_8_uuid()
        row.save(update_fields=["public_uuid"])


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0011_test_public_uuid'),
    ]

    operations = [
        # omit reverse_code=... if you don't want the migration to be reversible.
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
    ]
