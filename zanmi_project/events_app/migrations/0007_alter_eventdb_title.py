# Generated by Django 5.2 on 2025-04-18 03:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events_app", "0006_eventdb_location_eventdb_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eventdb",
            name="title",
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]
