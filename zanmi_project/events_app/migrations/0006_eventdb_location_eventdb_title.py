# Generated by Django 5.2 on 2025-04-18 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events_app", "0005_notificationdb"),
    ]

    operations = [
        migrations.AddField(
            model_name="eventdb",
            name="location",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="eventdb",
            name="title",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
